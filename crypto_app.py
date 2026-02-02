import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. STABLE CONFIG (Optimized Refresh) ---
st.set_page_config(page_title="JARVIS SUPREME v56", layout="wide")
# 2 सेकंड का रिफ्रेश सर्वर एरर को रोकने के लिए सबसे बेस्ट है
st_autorefresh(interval=2000, key="jarvis_v56_supreme")

# --- 🔊 2. EMERGENCY WAKE-UP & SIREN ---
def jarvis_emergency_system(text, alert_type="normal"):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(err => {{}}); }}
    window.speechSynthesis.cancel();
    var siren = new Audio('{siren_url}'); siren.play();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN'; window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: SUPREME COMMAND v56.0</h1>", unsafe_allow_html=True)

# Persistent States
for key in ["st_last", "st_ep", "r_last", "r_ep", "st_prev_ltp", "r_prev_ltp"]:
    if key not in st.session_state: st.session_state[key] = "" if "last" in key else 0.0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (JAVED & KARISHMA) ---
with col_st:
    st.subheader("📈 NSE SIGNAL")
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    try:
        # 5 दिन का डेटा ताकि EMA200 स्टेबल रहे
        df_st = yf.download(asset_st, period="5d", interval="1m", progress=False)
        if not df_st.empty and len(df_st) > 200:
            df_st['E9'] = df_st['Close'].ewm(span=9).mean()
            df_st['E21'] = df_st['Close'].ewm(span=21).mean()
            df_st['E200'] = df_st['Close'].ewm(span=200).mean()
            
            ltp = float(df_st['Close'].iloc[-1])
            e9, e21, e200 = float(df_st['E9'].iloc[-1]), float(df_st['E21'].iloc[-1]), float(df_st['E200'].iloc[-1])

            # Signal Logic
            is_call = bool(e9 > e21 and ltp > e200)
            is_put = bool(e9 < e21 and ltp < e200)

            if is_call and st.session_state.st_last != "CALL":
                st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
                jarvis_emergency_system(f"NSE Alert: Call Entry detected at {ltp}")
            elif is_put and st.session_state.st_last != "PUT":
                st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
                jarvis_emergency_system(f"NSE Alert: Put Entry detected at {ltp}")

            # Display
            c1, c2 = st.columns(2)
            c1.metric("LIVE PRICE", f"₹{round(ltp,2)}")
            c2.metric("SIGNAL STATUS", st.session_state.st_last if st.session_state.st_last else "WAITING")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_st, use_container_width=True)
    except: st.info("📡 NSE Satellite Syncing...")

# --- ₿ SECTION B: CRYPTO (JARVIS R) ---
with col_cr:
    st.subheader("₿ CRYPTO SIGNAL")
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        res = requests.get(url, timeout=3).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = df_cr['close'].ewm(span=9).mean()
            df_cr['E21'] = df_cr['close'].ewm(span=21).mean()
            df_cr['E200'] = df_cr['close'].ewm(span=200).mean()
            
            ltp_r = float(df_cr['close'].iloc[-1])
            e9_r, e21_r, e200_r = float(df_cr['E9'].iloc[-1]), float(df_cr['E21'].iloc[-1]), float(df_cr['E200'].iloc[-1])

            if e9_r > e21_r and ltp_r > e200_r and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_r
                jarvis_emergency_system("Crypto Alert: Bitcoin Call Buy")
            elif e9_r < e21_r and ltp_r < e200_r and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r
                jarvis_emergency_system("Crypto Alert: Bitcoin Put Buy")

            c1, c2 = st.columns(2)
            c1.metric("BTC PRICE", f"${ltp_r}")
            c2.metric("SIGNAL STATUS", st.session_state.r_last if st.session_state.r_last else "WAITING")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting to Crypto Satellite...")

# --- 🛡️ RESET ---
if st.button("🔄 Reset Hunter System"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
