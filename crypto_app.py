import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS MASTER v104", layout="wide")
st_autorefresh(interval=4000, key="jarvis_v104_supreme")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang = 'hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 2. STATE & MEMORY (Zero Movement) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_lock": False, "cr_lock": False, "st_sig": "SCANNING", "cr_sig": "SCANNING",
        "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0, "balance": 120.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏛️ JARVIS MASTER v104.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS SYSTEM"):
    jarvis_speak("नमस्ते राजवीर सर, बैकअप डेटा सिस्टम एक्टिवेट हो गया है।")

col_st, col_cr = st.columns(2)

# --- 📈 NSE SECTION (With Backup Logic) ---
with col_st:
    st.header("📈 NSE STOCK")
    try:
        # --- PRIMARY SOURCE: Yahoo Finance ---
        data_st = yf.download("^NSEI", period="2d", interval="1m", progress=False)
        if data_st.empty:
            # --- BACKUP SOURCE: Direct Ticker ---
            data_st = yf.Ticker("^NSEI").history(period="2d", interval="1m")
            
        if not data_st.empty:
            df_st = data_st.copy()
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            ltp = round(df_st['Close'].iloc[-1], 2)

            if not st.session_state.st_lock:
                if df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp, "st_sl": ltp-50, "st_tg": ltp+250, "st_lock": True})
                    jarvis_speak("एन एस ई कॉल लॉक्ड")
                elif df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp, "st_sl": ltp+50, "st_tg": ltp-250, "st_lock": True})
                    jarvis_speak("एन एस ई पुट लॉक्ड")

            st.metric("NIFTY 50", f"₹{ltp}")
            st.success(f"📌 {st.session_state.st_sig} | Entry: {st.session_state.st_ep}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_st, use_container_width=True)
    except:
        st.info("📡 NSE डेटा का बैकअप लोड हो रहा है...")

# --- ₿ CRYPTO SECTION (With Backup Logic) ---
with col_cr:
    st.header("₿ CRYPTO MARKET")
    try:
        # --- PRIMARY SOURCE: Binance ---
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=3).json()
        ltp_cr = round(float(res['price']), 2)
    except:
        try:
            # --- BACKUP SOURCE: CryptoCompare ---
            res = requests.get("https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD").json()
            ltp_cr = float(res['USD'])
        except:
            ltp_cr = 0.0

    if ltp_cr > 0:
        if not st.session_state.cr_lock:
            st.session_state.update({"cr_sig": "READY", "cr_ep": ltp_cr, "cr_sl": ltp_cr-200, "cr_lock": True})
            jarvis_speak("क्रिप्टो सिग्नल तैयार")

        st.metric("BTC PRICE", f"${ltp_cr}")
        qty = round((st.session_state.balance * 10) / ltp_cr, 4)
        st.warning(f"💰 Qty: {qty} BTC | Bal: $120")
        st.info(f"📌 {st.session_state.cr_sig} | Entry: {st.session_state.cr_ep}")
    else:
        st.error("📡 सभी API बिजी हैं। कृपया रिफ्रेश करें।")

st.write("---")
if st.button("🔄 FULL SYSTEM RESET"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
