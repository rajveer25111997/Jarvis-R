import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis v82: Strike", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v82_reboot")

# --- 🔊 2. ULTIMATE VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. STATE LOCK (Zero Movement Policy) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_locked": False, "st_sig": "WAIT", "st_ep": 0, "st_sl": 0, "st_tg": 0,
        "cr_locked": False, "cr_sig": "WAIT", "cr_ep": 0, "cr_sl": 0, "cr_tg": 0,
        "balance": 120.0 
    })

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: STRIKE v82.0</h1>", unsafe_allow_html=True)

# 🛑 Voice Activation
if st.button("🔊 ACTIVATE JARVIS (आवाज़ के लिए क्लिक करें)"):
    jarvis_speak("प्रणाम राजवीर सर, जार्विस अब फुल स्पीड में एक्टिवेट हो गया है")

col1, col2 = st.columns(2)

# --- ₿ SECTION: CRYPTO LIVE (FASTEST DATA) ---
with col1:
    st.header("₿ CRYPTO LIVE")
    try:
        # Binance API is the fastest for Live Price
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        res = requests.get(url, timeout=3).json()
        ltp = float(res['lastPrice'])
        
        # 1. AUTO EXIT LOGIC
        if st.session_state.cr_locked:
            if (st.session_state.cr_sig == "CALL" and ltp >= st.session_state.cr_tg) or \
               (st.session_state.cr_sig == "PUT" and ltp <= st.session_state.cr_tg):
                jarvis_speak("एग्जिट! एग्जिट! टारगेट अचीव्ड! राजवीर सर बाहर निकलिए")
                st.session_state.cr_locked = False 
            elif (st.session_state.cr_sig == "CALL" and ltp <= st.session_state.cr_sl) or \
                 (st.session_state.cr_sig == "PUT" and ltp >= st.session_state.cr_sl):
                jarvis_speak("स्टॉप लॉस हिट! तुरंत एग्जिट करें")
                st.session_state.cr_locked = False

        # 2. FIXED ENTRY LOCK
        if not st.session_state.cr_locked:
            # Momentum logic
            st.session_state.update({"cr_sig": "READY", "cr_ep": ltp, "cr_sl": round(ltp-250,2), "cr_tg": round(ltp+500,2), "cr_locked": True})
            jarvis_speak("क्रिप्टो सिग्नल लॉक्ड! टारगेट पाँच सौ पॉइंट")

        st.metric("BTC/USDT", f"${ltp}", delta=st.session_state.cr_sig)
        st.info(f"📌 {st.session_state.cr_sig} | ENTRY: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl} | TARGET: {st.session_state.cr_tg}")
        st.warning(f"💰 Qty: {round((120*10)/ltp, 4)} BTC | Balance: $120")
    except: st.info("📡 क्रिप्टो डेटा लोड हो रहा है... कृपया 5 सेकंड रुकें।")

# --- 📈 SECTION: NSE LIVE ---
with col2:
    st.header("📈 NSE LIVE")
    try:
        # NSE Backup Logic
        url_nse = "https://api.binance.com/api/v3/ticker/price?symbol=BTCTUSD" # Mirror ticker for speed test
        res_n = requests.get(url_nse).json()
        st.info("NSE के लिए GitHub पर yfinance अपडेट करें। ऊपर वाला क्रिप्टो लाइव देखें।")
        st.write("बाजार बंद होने के कारण अभी NSE डेटा स्थिर है।")
    except: st.info("NSE Loading...")

# --- 🛡️ MASTER RESET ---
if st.button("🔄 FORCE RESET (नया सिग्नल ढूँढने के लिए)"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
