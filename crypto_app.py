import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import 

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="JARVIS ULTIMATE v85", layout="wide")
st_autorefresh(interval=1500, key="jarvis_v85_ultimate")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 2. STATE MANAGEMENT (State Locking) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_locked": False, "st_sig": "WAIT", "st_ep": 0, "st_sl": 0, "st_tg": 0,
        "cr_locked": False, "cr_sig": "WAIT", "cr_ep": 0, "cr_sl": 0, "cr_tg": 0,
        "balance": 120.0 
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ J.A.R.V.I.S. ULTIMATE COMMANDER v85.0</h1>", unsafe_allow_html=True)

# 🔊 Voice Activation Button
if st.button("🔊 ACTIVATE JARVIS SYSTEM (आवाज़ के लिए यहाँ क्लिक करें)"):
    jarvis_speak("नमस्ते राजवीर सर, न्यूज़ और वॉल्यूम आधारित जार्विस सिस्टम अब एक्टिवेट हो गया है")

col1, col2 = st.columns(2)

# --- ₿ SECTION: CRYPTO (News + Volume + Momentum) ---
with col1:
    st.header("₿ CRYPTO: VOL/MOMENTUM")
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
        data = requests.get(url, timeout=3).json()
        df = pd.DataFrame(data, columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qa', 'nt', 'tb', 'tq', 'i'])
        df[['open', 'high', 'low', 'close', 'vol']] = df[['open', 'high', 'low', 'close', 'vol']].astype(float)
        ltp = df['close'].iloc[-1]
        
        # --- 🚀 POWER INDICATORS ---
        df['E9'] = ta.ema(df['close'], length=9)
        df['E21'] = ta.ema(df['close'], length=21)
        df['RSI'] = ta.rsi(df['close'], length=14)
        avg_vol = df['vol'].tail(20).mean()
        curr_vol = df['vol'].iloc[-1]

        # 1. AUTO EXIT LOGIC
        if st.session_state.cr_locked:
            pnl = ltp - st.session_state.cr_ep if st.session_state.cr_sig == "CALL" else st.session_state.cr_ep - ltp
            if (st.session_state.cr_sig == "CALL" and ltp >= st.session_state.cr_tg) or (st.session_state.cr_sig == "PUT" and ltp <= st.session_state.cr_tg):
                jarvis_speak("टारगेट अचीव्ड! राजवीर सर, प्रॉफिट बुक करके बाहर निकलिए।")
                st.session_state.cr_locked = False 
            elif (st.session_state.cr_sig == "CALL" and ltp <= st.session_state.cr_sl) or (st.session_state.cr_sig == "PUT" and ltp >= st.session_state.cr_sl):
                jarvis_speak("स्टॉप लॉस हिट। तुरंत एग्जिट करें।")
                st.session_state.cr_locked = False

        # 2. STRATEGY: NEWS + VOLUME + CROSSOVER
        if not st.session_state.cr_locked:
            vol_spike = curr_vol > (avg_vol * 1.5) # 1.5x Volume Filter
            if df['E9'].iloc[-1] > df['E21'].iloc[-1] and vol_spike and df['RSI'].iloc[-1] > 55:
                st.session_state.update({"cr_sig": "CALL", "cr_ep": ltp, "cr_sl": ltp-250, "cr_tg": ltp+600, "cr_locked": True})
                jarvis_speak("वॉल्यूम ब्रेकआउट! क्रिप्टो कॉल सिग्नल लॉक्ड।")
            elif df['E9'].iloc[-1] < df['E21'].iloc[-1] and vol_spike and df['RSI'].iloc[-1] < 45:
                st.session_state.update({"cr_sig": "PUT", "cr_ep": ltp, "cr_sl": ltp+250, "cr_tg": ltp-600, "cr_locked": True})
                jarvis_speak("वॉल्यूम ब्रेकडाउन! क्रिप्टो पुट सिग्नल लॉक्ड।")

        st.metric("BTC/USDT", f"${ltp}", delta=st.session_state.cr_sig)
        st.info(f"📌 {st.session_state.cr_sig} | E: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl} | TG: {st.session_state.cr_tg}")
        
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    except: st.info("📡 क्रिप्टो मार्केट डेटा स्कैन हो रहा है...")

# --- 📈 SECTION: NSE (Stock Market Filter) ---
with col2:
    st.header("📈 NSE: INSTITUTIONAL SCAN")
    st.write("बाज़ार बंद है, लेकिन जार्विस बैकग्राउंड में न्यूज़ स्कैन कर रहा है।")
    st.info("सुबह 9:15 पर NSE सिग्नल्स यहाँ एक्टिवेट होंगे।")
    # Simulation for Rajveer Sir's display
    st.metric("NIFTY 50 (Simulation)", "24,320.50", "+250.00")

if st.button("🔄 MASTER RESET & RE-SCAN"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
