import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- 🎯 1. SUPREME SETTINGS ---
st.set_page_config(page_title="JARVIS MASTER v103", layout="wide")
# रिफ्रेश रेट को थोडा बढ़ा दिया है ताकि API ब्लॉक न हो
st_autorefresh(interval=5000, key="jarvis_v103_final")

# --- 🔊 2. NO-FAIL VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"""<script>
        window.speechSynthesis.cancel();
        var m = new SpeechSynthesisUtterance('{text}');
        m.lang = 'hi-IN'; m.rate = 1.0;
        window.speechSynthesis.speak(m);
        </script>"""
        st.components.v1.html(js, height=0)

# --- 🧠 3. STABILITY MANAGER (Hard Locking Logic) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_lock": False, "cr_lock": False, 
        "st_sig": "SCANNING", "cr_sig": "SCANNING",
        "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0,
        "cr_ep": 0.0, "cr_sl": 0.0, "cr_tg": 0.0,
        "balance": 120.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS ULTIMATE FINAL v103.0</h1>", unsafe_allow_html=True)

# आवाज़ के लिए ज़रूरी बटन
if st.button("🔊 ACTIVATE JARVIS SYSTEM"):
    jarvis_speak("प्रणाम राजवीर सर, मास्टर सिस्टम तैयार है।")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (Javed/Karishma Logic) ---
with col_st:
    st.header("📈 NSE STOCK")
    asset_st = st.sidebar.selectbox("Select NSE", ["^NSEI", "^NSEBANK"], key="st_box")
    try:
        # yfinance डेटा लेने का सबसे सुरक्षित तरीका
        data_st = yf.download(asset_st, period="3d", interval="1m", progress=False)
        if not data_st.empty:
            df_st = data_st.copy()
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            df_st['E200'] = ta.ema(df_st['Close'], length=200)
            ltp = round(df_st['Close'].iloc[-1], 2)

            if not st.session_state.st_lock:
                is_call = df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp > df_st['E200'].iloc[-1]
                is_put = df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp < df_st['E200'].iloc[-1]
                
                if is_call:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp, "st_sl": ltp-50, "st_tg": ltp+250, "st_lock": True})
                    jarvis_speak("एन एस ई कॉल सिग्नल लॉक्ड")
                elif is_put:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp, "st_sl": ltp+50, "st_tg": ltp-250, "st_lock": True})
                    jarvis_speak("एन एस ई पुट सिग्नल लॉक्ड")

            st.metric(f"{asset_st} LIVE", f"₹{ltp}")
            st.success(f"📌 {st.session_state.st_sig} | ENTRY: {st.session_state.st_ep} | SL: {st.session_state.st_sl}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_st, use_container_width=True)
        else:
            st.info("📡 NSE डेटा का इंतज़ार...")
    except Exception as e:
        st.error(f"NSE API Busy. Retrying...")

# --- ₿ SECTION B: CRYPTO (The No-Crash Logic) ---
with col_cr:
    st.header("₿ CRYPTO MARKET")
    try:
        # KeyError से बचने के लिए Binance API का बैकअप इस्तेमाल किया है
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url, timeout=5).json()
        
        if 'price' in res:
            ltp_cr = round(float(res['price']), 2)
            
            # सिर्फ तभी सिग्नल लो जब लॉक न हो
            if not st.session_state.cr_lock:
                # 0 से स्टार्ट करने वाले पुराने पॉइंट्स के साथ फिक्स्ड एंट्री
                st.session_state.update({"cr_sig": "READY", "cr_ep": ltp_cr, "cr_sl": ltp_cr-200, "cr_tg": ltp_cr+600, "cr_lock": True})
                jarvis_speak("क्रिप्टो डेटा अपडेटेड")

            st.metric("BTC PRICE", f"${ltp_cr}")
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Qty: {qty} BTC | Capital: $120")
            st.info(f"📌 {st.session_state.cr_sig} | ENTRY: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl}")
        else:
            st.error("📡 Crypto API Error. Please Wait.")
    except:
        st.info("📡 क्रिप्टो बैकग्राउंड स्कैनिंग...")

# --- 🛡️ MASTER SYSTEM RESET ---
st.write("---")
if st.button("🔄 FULL SYSTEM RESET (New Trade Scan)"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
