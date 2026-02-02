import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS v80: UNBEATABLE", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v80")

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

# --- 🧠 3. STATE LOCK (Hilega Nahi) ---
if "st_lock" not in st.session_state:
    st.session_state.update({
        "st_lock": False, "cr_lock": False, 
        "st_sig": "SCANNING", "cr_sig": "SCANNING",
        "st_ep": 0, "st_sl": 0, "st_tg": 0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS: UNBEATABLE v80.0</h1>", unsafe_allow_html=True)

# 🛑 आवाज़ चालू करने का बटन (Must Click)
if st.button("🔊 ACTIVATE JARVIS (आवाज़ के लिए यहाँ क्लिक करें)"):
    jarvis_speak("नमस्ते राजवीर सर, जार्विस अब आपकी सेवा में पूरी तरह तैयार है")

col1, col2 = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (Nifty/BankNifty) ---
with col1:
    st.header("📈 NSE MARKET")
    asset = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK"])
    try:
        df = yf.download(asset, period="2d", interval="1m", progress=False)
        if not df.empty:
            ltp = round(df['Close'].iloc[-1], 2)
            df['E9'] = ta.ema(df['Close'], length=9)
            df['E21'] = ta.ema(df['Close'], length=21)

            if not st.session_state.st_lock:
                if df['E9'].iloc[-1] > df['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp, "st_sl": ltp-50, "st_tg": ltp+250, "st_lock": True})
                    jarvis_speak("एन एस ई कॉल सिग्नल लॉक्ड")
                elif df['E9'].iloc[-1] < df['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp, "st_sl": ltp+50, "st_tg": ltp-250, "st_lock": True})
                    jarvis_speak("एन एस ई पुट सिग्नल लॉक्ड")

            st.metric(f"LIVE {asset}", f"₹{ltp}", delta=st.session_state.st_sig)
            st.success(f"📌 {st.session_state.st_sig} | ENTRY: {st.session_state.st_ep} | SL: {st.session_state.st_sl} | TG: {st.session_state.st_tg}")
            
            # Candlestick Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
    except: st.info("📡 डेटा लोड हो रहा है...")

# --- ₿ SECTION B: CRYPTO (Bitcoin) ---
with col2:
    st.header("₿ CRYPTO MARKET")
    try:
        df_cr = yf.download("BTC-USD", period="2d", interval="1m", progress=False)
        if not df_cr.empty:
            ltp_c = round(df_cr['Close'].iloc[-1], 2)
            
            if not st.session_state.cr_lock:
                st.session_state.update({"cr_sig": "READY", "cr_ep": ltp_c, "cr_lock": True})

            st.metric("BITCOIN", f"${ltp_c}")
            st.warning(f"💰 Balance: $120 | Qty: {round(1200/ltp_c, 4)} BTC")
            st.info(f"📌 {st.session_state.cr_sig} | Entry: {st.session_state.cr_ep}")
            
            fig_c = go.Figure(data=[go.Candlestick(x=df_cr.index, open=df_cr['Open'], high=df_cr['High'], low=df_cr['Low'], close=df_cr['Close'])])
            fig_c.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_c, use_container_width=True)
    except: st.info("📡 क्रिप्टो डेटा लोड हो रहा है...")

# --- 🛡️ MASTER RESET ---
if st.button("🔄 UNLOCK & RESET SYSTEM"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
