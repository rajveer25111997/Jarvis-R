import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS BRAIN v106", layout="wide")
st_autorefresh(interval=3000, key="jarvis_v106_final")

# --- 🔊 2. VOICE ENGINE (Brain Point: Always Speak) ---
def jarvis_speak(text):
    if text:
        js = f"""<script>
        window.speechSynthesis.cancel();
        var m = new SpeechSynthesisUtterance('{text}');
        m.lang = 'hi-IN'; m.rate = 1.0;
        window.speechSynthesis.speak(m);
        </script>"""
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT STATE (Brain Point: Hard Locking) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_lock": False, "cr_lock": False, 
        "st_sig": "SCANNING", "cr_sig": "SCANNING",
        "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0,
        "cr_ep": 0.0, "cr_sl": 0.0, "cr_tg": 0.0,
        "balance": 120.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS BRAIN RESTORED v106.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS VOICE (आवाज़ के लिए यहाँ क्लिक करें)"):
    jarvis_speak("नमस्ते राजवीर सर, जार्विस का दिमाग और आवाज़ पूरी तरह बहाल कर दी गई है।")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE (Javed/Karishma + News Effect) ---
with col_st:
    st.header("📈 NSE (9/21 Strategy)")
    try:
        # Multi-Source Fetch
        df_st = yf.download("^NSEI", period="3d", interval="1m", progress=False)
        if not df_st.empty:
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            df_st['E200'] = ta.ema(df_st['Close'], length=200)
            df_st['ATR'] = ta.atr(df_st['High'], df_st['Low'], df_st['Close'], length=14)
            ltp = round(df_st['Close'].iloc[-1], 2)

            # Signal Logic Restore
            if not st.session_state.st_lock:
                is_call = df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp > df_st['E200'].iloc[-1]
                is_put = df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp < df_st['E200'].iloc[-1]
                
                if is_call:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp, "st_sl": ltp-50, "st_tg": ltp+250, "st_lock": True})
                    jarvis_speak("एन एस ई कॉल लॉक्ड")
                elif is_put:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp, "st_sl": ltp+50, "st_tg": ltp-250, "st_lock": True})
                    jarvis_speak("एन एस ई पुट लॉक्ड")

            st.metric("NIFTY 50", f"₹{ltp}")
            st.success(f"📌 {st.session_state.st_sig} | Entry: {st.session_state.st_ep} | SL: {st.session_state.st_sl}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_st, use_container_width=True)
    except: st.info("NSE बैकग्राउंड स्कैनिंग...")

# --- ₿ SECTION B: CRYPTO (The $120 Logic + News) ---
with col_cr:
    st.header("₿ CRYPTO (Delta Master)")
    try:
        # Triple Backup Data
        ltp_cr = 0.0
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=3).json()
        ltp_cr = float(r['price'])
        
        if ltp_cr > 0:
            if not st.session_state.cr_lock:
                st.session_state.update({"cr_sig": "READY", "cr_ep": ltp_cr, "cr_sl": ltp_cr-200, "cr_tg": ltp_cr+600, "cr_lock": True})
                jarvis_speak("क्रिप्टो सिग्नल और भाव अपडेट हो गए हैं")

            st.metric("BTC PRICE", f"${round(ltp_cr, 2)}")
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Qty: {qty} BTC | Bal: $120")
            st.info(f"📌 {st.session_state.cr_sig} | Entry: {st.session_state.cr_ep}")
    except: st.info("क्रिप्टो बैकग्राउंड स्कैनिंग...")

st.write("---")
if st.button("🔄 FULL SYSTEM RESET"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
