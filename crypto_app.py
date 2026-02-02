import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="Jarvis Final Fix", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v77")

# --- 🔊 2. आवाज़ का पक्का इलाज ---
def jarvis_speak(text):
    if text:
        js_code = f"""
        <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        window.speechSynthesis.speak(msg);
        </script>
        """
        st.components.v1.html(js_code, height=0)

# --- 🧠 3. डेटा को लॉक करने वाला सिस्टम ---
if "st_lock" not in st.session_state:
    st.session_state.update({"st_lock": False, "cr_lock": False, "st_sig": "SCANNING", "cr_sig": "SCANNING"})

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: FINAL v77.0</h1>", unsafe_allow_html=True)

# 🛑 आवाज़ के लिए यह बटन दबाना ज़रूरी है
if st.button("🔊 CLICK HERE TO START VOICE (आवाज़ के लिए यहाँ दबाएँ)"):
    jarvis_speak("नमस्ते राजवीर सर, जार्विस अब आपकी सेवा में हाज़िर है")

col_st, col_cr = st.columns(2)

# --- 📈 NSE SECTION ---
with col_st:
    st.header("📈 NSE")
    try:
        # Fast Fetch
        df_st = yf.download("^NSEI", period="2d", interval="1m", progress=False)
        if not df_st.empty:
            ltp = round(df_st['Close'].iloc[-1], 2)
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)

            if not st.session_state.st_lock:
                if df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp, "st_sl": ltp-50, "st_tg": ltp+200, "st_lock": True})
                    jarvis_speak("एन एस ई कॉल सिग्नल लॉक्ड")
                elif df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp, "st_sl": ltp+50, "st_tg": ltp-200, "st_lock": True})
                    jarvis_speak("एन एस ई पुट सिग्नल लॉक्ड")

            st.metric("NIFTY 50", f"₹{ltp}")
            st.success(f"📌 {st.session_state.st_sig} | Entry: {st.session_state.get('st_ep', 0)} | SL: {st.session_state.get('st_sl', 0)}")
    except: st.info("NSE डेटा लोड हो रहा है...")

# --- ₿ CRYPTO SECTION ---
with col_cr:
    st.header("₿ CRYPTO")
    try:
        # Backup API for Crypto
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url).json()
        ltp_cr = float(res['price'])
        
        # Crypto Logic (Locked)
        if not st.session_state.cr_lock:
            # Simple Trend Logic for Fast Loading
            st.session_state.update({"cr_sig": "READY", "cr_ep": ltp_cr, "cr_sl": ltp_cr-150, "cr_tg": ltp_cr+400, "cr_lock": True})
            jarvis_speak("क्रिप्टो डेटा अपडेटेड")

        st.metric("BTC/USDT", f"${round(ltp_cr, 2)}")
        st.info(f"📌 {st.session_state.cr_sig} | E: {st.session_state.get('cr_ep', 0)} | Qty: {round(1200/ltp_cr, 4)}")
    except: st.info("क्रिप्टो डेटा इंतज़ार में है...")

# --- 🛡️ RESET ---
if st.button("🔄 RESET ALL"):
    st.session_state.st_lock = False; st.session_state.cr_lock = False
    st.rerun()
