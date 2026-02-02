import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. SUPREME CONFIG (1-SEC REFRESH) ---
st.set_page_config(page_title="JARVIS DUAL: PROTECTOR", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v45_ultimate")

# --- 🔊 2. EMERGENCY SIREN & VOICE ENGINE ---
def jarvis_emergency_system(text, alert_type="normal"):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(err => {{}}); }}
    window.speechSynthesis.cancel();
    var siren = new Audio('{siren_url}'); siren.play();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN'; msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🧠 3. DATA & WHALE RADAR ENGINE ---
def get_data(symbol, is_crypto=False):
    try:
        if is_crypto:
            url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=300"
            res = requests.get(url, timeout=2).json()
            df = pd.DataFrame(res['Data']['Data'])
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.rename(columns={'close': 'Close', 'high': 'High', 'low': 'Low', 'open': 'Open', 'volumeto': 'Volume'}, inplace=True)
        else:
            df = yf.download(symbol, period="5d", interval="1m", progress=False)
        return df
    except: return pd.DataFrame()

# --- 🎨 4. BRANDING & STATE ---
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS DUAL: ULTIMATE COMMAND CENTER</h1>", unsafe_allow_html=True)

if "st_last" not in st.session_state: 
    keys = ["st_last", "st_ep", "r_last", "r_ep", "st_wins", "st_loss", "r_wins", "r_loss"]
    for k in keys: st.session_state[k] = "" if "last" in k else 0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE) ---
with col_st:
    st.subheader("📈 STOCK: JAVED & KARISHMA")
    asset_st = st.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = get_data(asset_st)
    
    if not df_st.empty and len(df_st) > 100:
        # Indicators
        df_st['E9'] = ta.ema(df_st['Close'], length=9)
        df_st['E21'] = ta.ema(df_st['Close'], length=21)
        df_st['E200'] = ta.ema(df_st['Close'], length=200)
        ltp_st = float(df_st['Close'].iloc[-1])
        
        # Whale Radar (Volume Spike detection)
        avg_vol = df_st['Volume'].tail(20).mean()
        whale_alert = df_st['Volume'].iloc[-1] > (avg_vol * 3)

        # Javed Strategy (9/21 Cross)
        is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp_st > df_st['E200'].iloc[-1])
        is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp_st < df_st['E200'].iloc[-1])

        if is_call and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp_st
            jarvis_emergency_system(f"Rajveer Sir, Call Entry! Strike: {round(ltp_st/100)*100} CE", "normal")
        elif is_put and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp_st
            jarvis_emergency_system(f"Rajveer Sir, Put Entry! Strike: {round(ltp_st/100)*100} PE", "normal")

        # Karishma (Smart Stop Loss)
        if st.session_state.st_ep > 0:
            pnl = ltp_st - st.session_state.st_ep if st.session_state.st_last == "CALL" else st.session_state.st_ep - ltp_st
            if pnl < -25: # Karishma SL active
                jarvis_emergency_system("Karishma SL Hit! Exit Stock Trade.", "emergency")
                st.session_state.st_ep = 0; st.session_state.st_last = "SL EXIT"

        st.metric(f"NSE {asset_st}", f"₹{ltp_st}", delta=f"Signal: {st.session_state.st_last}")
        if whale_alert: st.warning("🐋 WHALE RADAR: Large Volume Detected!")
        
        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.add_trace(go.Scatter(x=df_st.index, y=df_st['E200'], name='200 EMA', line=dict(color='orange')))
        fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO (JARVIS R) ---
with col_cr:
    st.subheader("₿ CRYPTO: HUNTER MODE")
    df_cr = get_data("BTC", is_crypto=True)
    
    if not df_cr.empty and len(df_cr) > 100:
        df_cr['E9'] = ta.ema(df_cr['Close'], length=9)
        df_cr['E21'] = ta.ema(df_cr['Close'], length=21)
        df_cr['E200'] = ta.ema(df_cr['Close'], length=200)
        ltp_cr = float(df_cr['Close'].iloc[-1])

        is_call_r = bool(df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_cr > df_cr['E200'].iloc[-1])
        is_put_r = bool(df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_cr < df_cr['E200'].iloc[-1])

        if is_call_r and st.session_state.r_last != "CALL":
            st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_cr
            jarvis_emergency_system("Jarvis R: Bitcoin Call Buy!", "normal")
        elif is_put_r and st.session_state.r_last != "PUT":
            st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_cr
            jarvis_emergency_system("Jarvis R: Bitcoin Put Buy!", "normal")

        # Hunter PNL Alerts (250-500 Points)
        if st.session_state.r_ep > 0:
            pnl_r = ltp_cr - st.session_state.r_ep if st.session_state.r_last == "CALL" else st.session_state.r_ep - ltp_cr
            if pnl_r >= 300:
                jarvis_emergency_system("Rajveer Sir, 300 Point Jackpot! Ruko nahi!", "normal")
            elif pnl_r < -150:
                jarvis_emergency_system("Crypto SL Hit! Exit Now.", "emergency")
                st.session_state.r_ep = 0; st.session_state.r_last = "SL EXIT"

        st.metric("BTC PRICE", f"${ltp_cr}", delta=f"Signal: {st.session_state.r_last}")
        fig_cr = go.Figure(data=[go.Candlestick(x=df_cr.index, open=df_cr['Open'], high=df_cr['High'], low=df_cr['Low'], close=df_cr['Close'])])
        fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_cr, use_container_width=True)

# --- 🏥 5. PORTFOLIO DOCTOR ---
st.write("---")
st.subheader("🏥 PORTFOLIO DOCTOR & PERFORMANCE")
d1, d2, d3 = st.columns(3)
with d1:
    st.write("**Automatic Strike Price Selection:**")
    if st.session_state.st_ep > 0:
        strike = round(st.session_state.st_ep / 100) * 100
        st.code(f"ATM {st.session_state.st_last}: {strike}")
with d2:
    st.write("**Portfolio Health:**")
    st.success("System Healthy 🟢") if not df_st.empty else st.error("Data Lag detected 🔴")
with d3:
    if st.button("🔄 Reset Master Terminal"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

