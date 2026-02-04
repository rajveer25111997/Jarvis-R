import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG (1s Refresh for Crypto Speed) ---
st.set_page_config(page_title="Crypto Jarvis v160", layout="wide")
st_autorefresh(interval=1000, key="crypto_jarvis_1s")

# --- 🔊 2. MASTER VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; m.rate=1.1; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT BRAIN & PORTFOLIO DOCTOR ---
if "init" not in st.session_state:
    st.session_state.update({
        "locked": False, "sig": "SCANNING", 
        "ep": 0.0, "sl": 0.0, "tg": 0.0,
        "health": "GOOD", "bal": 120.0, "last_msg": ""
    })

st.markdown("<h1 style='text-align:center; color:#F7931A;'>₿ CRYPTO JARVIS COMMANDER v160.0</h1>", unsafe_allow_html=True)

# --- 📈 4. DIRECT BINANCE DATA ENGINE (No-Blink) ---
def fetch_crypto_data():
    try:
        # Fetching Bitcoin (BTC/USDT) from Binance
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
        res = requests.get(url, timeout=3).json()
        df = pd.DataFrame(res, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVol', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore'])
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        df.index = pd.to_datetime(df['Time'], unit='ms')
        return df[['Close', 'Volume']]
    except: return pd.DataFrame()

df = fetch_crypto_data()

# --- ⚙️ 5. INTEGRATING ALL 45 POINTS (Crypto Mode) ---
if not df.empty and len(df) > 21:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    df['E200'] = ta.ema(df['Close'], length=min(len(df), 200))
    
    # Whale Radar (Crypto Whale Alerts)
    vol_spike = df['Volume'].iloc[-1] > (df['Volume'].tail(15).mean() * 1.5)

    if not st.session_state.locked:
        e9, e21, e200 = df['E9'].iloc[-1], df['E21'].iloc[-1], df['E200'].iloc[-1]
        
        # Javed (9/21) + Whale Presence + Trend
        is_call = e9 > e21 and ltp > e200 and vol_spike
        is_put = e9 < e21 and ltp < e200 and vol_spike

        if is_call or is_put:
            side = "LONG (BUY)" if is_call else "SHORT (SELL)"
            # Karishma SL Logic (Crypto Volatility adjustment)
            sl_val = ltp - 150 if is_call else ltp + 150
            tg_val = ltp + 450 if is_call else ltp - 450
            
            st.session_state.update({
                "sig": side, "ep": ltp, "sl": sl_val, "tg": tg_val, "locked": True
            })
            jarvis_speak(f"राजवीर सर, क्रिप्टो व्हेल ने एंट्री ली है। {side} सिग्नल लॉक है।")

    else:
        # Portfolio Doctor & Emergency Siren Tracking
        profit = (ltp - st.session_state.ep) if "LONG" in st.session_state.sig else (st.session_state.ep - ltp)
        
        if profit <= -100: # Emergency Siren for Crypto
            st.session_state.health = "🆘 EXIT NOW!"
            if st.session_state.last_msg != "exit":
                jarvis_speak("इमरजेंसी सायरन! राजवीर सर, बिटकॉइन पलट गया है, तुरंत बाहर निकलें।")
                st.session_state.last_msg = "exit"
        elif profit >= 300:
            st.session_state.health = "🚀 JACKPOT HOLD"
        else:
            st.session_state.health = "✅ POSITION HEALTHY"

    # --- 📊 6. CRYPTO DASHBOARD ---
    c1, c2, c3 = st.columns(3)
    c1.metric("BITCOIN (BTC/USDT)", f"${ltp}")
    c2.success(f"📌 {st.session_state.sig} @ ${st.session_state.ep}")
    
    # Portfolio Doctor Box
    doc_clr = "red" if "EXIT" in st.session_state.health else "gold" if "JACKPOT" in st.session_state.health else "#00FF00"
    c3.markdown(f"<div style='background-color:{doc_clr}; padding:10px; border-radius:10px; color:black; font-weight:bold; text-align:center;'>DOCTOR: {st.session_state.health}</div>", unsafe_allow_html=True)

    # Risk Management Display
    st.write(f"### 📈 Profit/Loss: ${round(profit, 2) if st.session_state.locked else 0.0}")
    
    
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#F7931A', width=2))])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='EMA 9', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name='EMA 21', line=dict(color='cyan')))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📡 जार्विस 1 सेकंड की रफ़्तार से क्रिप्टो व्हेल और बिटकॉइन की चाल स्कैन कर रहा है...")

# --- 🛡️ MASTER RESET ---
if st.button("🔄 FULL SYSTEM RESET"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
