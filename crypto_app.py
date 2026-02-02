import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SURVIVOR CONFIG ---
st.set_page_config(page_title="JARVIS SURVIVOR v105", layout="wide")
st_autorefresh(interval=5000, key="jarvis_v105_survivor")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang = 'hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 2. IRON STATE ---
if "init" not in st.session_state:
    st.session_state.update({"st_lock": False, "cr_lock": False, "st_sig": "SCANNING", "cr_sig": "SCANNING", "st_ep": 0.0, "balance": 120.0})

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔥 JARVIS MASTER: THE SURVIVOR v105.0</h1>", unsafe_allow_html=True)

# --- 📈 SECTION A: NSE (Multi-Source Rescue) ---
with st.container():
    col_st, col_cr = st.columns(2)
    with col_st:
        st.header("📈 NSE STOCK")
        try:
            # TRY 1: Direct Download
            df_st = yf.download("^NSEI", period="1d", interval="1m", progress=False, timeout=10)
            if df_st.empty:
                # TRY 2: Fast Ticker
                df_st = yf.Ticker("^NSEI").history(period="1d", interval="1m")
            
            if not df_st.empty:
                ltp = round(df_st['Close'].iloc[-1], 2)
                st.metric("NIFTY 50", f"₹{ltp}")
                st.success(f"📌 {st.session_state.st_sig} | Entry: {st.session_state.st_ep}")
                
                fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
                fig_st.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_st, use_container_width=True)
            else:
                st.error("📡 NSE Primary down. Trying Global Mirror...")
        except:
            st.info("🔄 Re-connecting to NSE servers...")

# --- ₿ SECTION B: CRYPTO (Global Backup Engine) ---
    with col_cr:
        st.header("₿ CRYPTO MARKET")
        ltp_cr = 0.0
        # TRIPLE BACKUP CHECK
        sources = [
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            "https://api.coinbase.com/v2/prices/BTC-USD/spot",
            "https://api.coincap.io/v2/assets/bitcoin"
        ]
        
        for url in sources:
            try:
                res = requests.get(url, timeout=5).json()
                if 'price' in res: ltp_cr = float(res['price'])
                elif 'data' in res and 'amount' in res['data']: ltp_cr = float(res['data']['amount'])
                elif 'data' in res and 'priceUsd' in res['data']: ltp_cr = float(res['data']['priceUsd'])
                if ltp_cr > 0: break
            except: continue

        if ltp_cr > 0:
            st.metric("BTC PRICE", f"${round(ltp_cr, 2)}")
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Qty: {qty} BTC | Bal: $120")
        else:
            st.error("📡 All Global Crypto Nodes Busy. Retrying in 5s...")

st.write("---")
if st.button("🔄 EMERGENCY SYSTEM RESET"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
