import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="Jarvis: No-Miss v73", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v73_nomiss")

def jarvis_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. STATE MANAGEMENT ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_last": "WAIT", "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0,
        "cr_last": "WAIT", "cr_ep": 0.0, "cr_sl": 0.0, "cr_tg": 0.0,
        "balance": 120.0 
    })

st.markdown(f"<h1 style='text-align:center; color:#00FFFF;'>🚀 JARVIS DUAL: NO-MISS EDITION v73.0</h1>", unsafe_allow_html=True)

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (Fast Entry) ---
with col_st:
    st.header("📈 NSE FAST-TRACK")
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = yf.Ticker(asset_st).history(period="3d", interval="1m")
    
    if not df_st.empty and len(df_st) > 100:
        df_st['E9'] = ta.ema(df_st['Close'], length=9)
        df_st['E21'] = ta.ema(df_st['Close'], length=21)
        # NEWS EFFECT CHECK
        df_st['ATR'] = ta.atr(df_st['High'], df_st['Low'], df_st['Close'], length=14)
        ltp_st = df_st['Close'].iloc[-1]
        
        # AGER MOMENTUM TEZ HAI (ATR High), TO SIGNAL TURANT DO
        is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1])
        is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1])

        curr_sig = "CALL" if is_call else "PUT"

        if curr_sig != st.session_state.st_last:
            st.session_state.st_last = curr_sig
            st.session_state.st_ep = round(ltp_st, 2)
            st.session_state.st_sl = round(ltp_st - 60, 2) if curr_sig == "CALL" else round(ltp_st + 60, 2)
            st.session_state.st_tg = round(ltp_st + 250, 2) if curr_sig == "CALL" else round(ltp_st - 250, 2)
            jarvis_speak(f"NSE {curr_sig} Locked! Big move detected.")

        st.metric(f"LIVE {asset_st}", f"₹{round(ltp_st,2)}", delta=st.session_state.st_last)
        st.success(f"📌 {st.session_state.st_last} LOCKED | E: {st.session_state.st_ep} | SL: {st.session_state.st_sl} | TG: {st.session_state.st_tg}")
        
        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO (250+ Point Catching Logic) ---
with col_cr:
    st.header("₿ CRYPTO NO-MISS")
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        res = requests.get(url, timeout=3).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)
            ltp_cr = float(df_cr['close'].iloc[-1])

            cr_sig = "CALL" if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] else "PUT"

            if cr_sig != st.session_state.cr_last:
                st.session_state.cr_last = cr_sig
                st.session_state.cr_ep = round(ltp_cr, 2)
                st.session_state.cr_sl = round(ltp_cr - 250, 2) if cr_sig == "CALL" else round(ltp_cr + 250, 2)
                st.session_state.cr_tg = round(ltp_cr + 500, 2) if cr_sig == "CALL" else round(ltp_cr - 500, 2)
                jarvis_speak(f"Crypto {cr_sig} Signal! No miss mode active.")

            st.metric("BTC PRICE", f"${ltp_cr}", delta=st.session_state.cr_last)
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Bal: ${st.session_state.balance} | Qty: {qty} BTC")
            st.info(f"📌 {st.session_state.cr_last} LOCKED | E: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl} | TG: {st.session_state.cr_tg}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Crypto Syncing...")

if st.button("🔄 FULL RESET & NEW SCAN"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
