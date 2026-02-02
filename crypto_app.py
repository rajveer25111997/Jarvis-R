import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="Jarvis: Iron Final v76", layout="wide")
st_autorefresh(interval=3000, key="jarvis_v76_iron")

# --- 🔊 2. VOICE ENGINE (Permanent Fix) ---
def jarvis_speak(text):
    if text:
        js = f"""<script>
        window.speechSynthesis.cancel();
        var m = new SpeechSynthesisUtterance('{text}');
        m.lang = 'hi-IN'; m.rate = 1.0;
        window.speechSynthesis.speak(m);
        </script>"""
        st.components.v1.html(js, height=0)

# --- 🧠 3. STABILITY MANAGER ---
# Yeh hissa aapki entry ko hilega nahi
if "st_lock" not in st.session_state:
    st.session_state.update({"st_lock": False, "cr_lock": False, "bal": 120.0, "st_sig": "WAIT", "cr_sig": "WAIT"})

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: IRON FINAL v76.0</h1>", unsafe_allow_html=True)

# Voice Button
if st.button("🔊 ACTIVATE JARVIS VOICE (आवाज़ के लिए यहाँ क्लिक करें)"):
    jarvis_speak("प्रणाम राजवीर सर, जार्विस तैयार है")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK ---
with col_st:
    st.header("📈 NSE STOCK")
    asset_st = st.sidebar.selectbox("Select NSE", ["^NSEI", "^NSEBANK"], key="st_box")
    try:
        df_st = yf.Ticker(asset_st).history(period="3d", interval="1m")
        if not df_st.empty:
            ltp_st = round(df_st['Close'].iloc[-1], 2)
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)

            if not st.session_state.st_lock:
                if df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1]:
                    st.session_state.st_sig = "CALL"; st.session_state.st_ep = ltp_st
                    st.session_state.st_sl = ltp_st - 50; st.session_state.st_tg = ltp_st + 250
                    st.session_state.st_lock = True
                    jarvis_speak("एन एस ई कॉल लॉक्ड")
                elif df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1]:
                    st.session_state.st_sig = "PUT"; st.session_state.st_ep = ltp_st
                    st.session_state.st_sl = ltp_st + 50; st.session_state.st_tg = ltp_st - 250
                    st.session_state.st_lock = True
                    jarvis_speak("एन एस ई पुट लॉक्ड")

            st.metric(f"{asset_st}", f"₹{ltp_st}")
            st.success(f"📌 {st.session_state.st_sig} | Entry: {st.session_state.get('st_ep',0)} | SL: {st.session_state.get('st_sl',0)}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_st, use_container_width=True)
    except: st.info("📡 NSE डेटा लोड हो रहा है...")

# --- ₿ SECTION B: CRYPTO (The Crash Fix) ---
with col_cr:
    st.header("₿ CRYPTO MARKET")
    try:
        url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=200"
        res = requests.get(url).json()
        if 'Data' in res and 'Data' in res['Data']:
            df_cr = pd.DataFrame(res['Data']['Data'])
            ltp_cr = float(df_cr['close'].iloc[-1])
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)

            if not st.session_state.cr_lock:
                if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1]:
                    st.session_state.cr_sig = "CALL"; st.session_state.cr_ep = ltp_cr
                    st.session_state.cr_sl = ltp_cr - 200; st.session_state.cr_tg = ltp_cr + 600
                    st.session_state.cr_lock = True
                    jarvis_speak("क्रिप्टो कॉल लॉक्ड")
                elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1]:
                    st.session_state.cr_sig = "PUT"; st.session_state.cr_ep = ltp_cr
                    st.session_state.cr_sl = ltp_cr + 200; st.session_state.cr_tg = ltp_cr - 600
                    st.session_state.cr_lock = True
                    jarvis_speak("क्रिप्टो पुट लॉक्ड")

            st.metric("BTC PRICE", f"${ltp_cr}")
            st.warning(f"💰 Qty: {round((st.session_state.bal*10)/ltp_cr, 4)} BTC | Bal: $120")
            st.info(f"📌 {st.session_state.cr_sig} | E: {st.session_state.get('cr_ep',0)} | SL: {st.session_state.get('cr_sl',0)}")
        else: st.error("📡 API रिस्पांस नहीं दे रही, रिफ्रेश करें।")
    except: st.info("📡 क्रिप्टो डेटा इंतज़ार में है...")

# --- 🛡️ UNLOCK ---
if st.button("🔄 UNLOCK ALL"):
    st.session_state.st_lock = False; st.session_state.cr_lock = False
    st.rerun()
