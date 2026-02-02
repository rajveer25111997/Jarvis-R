import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="Jarvis: Master Commander", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v67_final")

def jarvis_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. STATE MANAGEMENT ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_last": "", "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0,
        "cr_last": "", "cr_ep": 0.0, "cr_sl": 0.0, "cr_tg": 0.0
    })

# --- 💰 3. CAPITAL INFO ($120) ---
CAPITAL = 120.0 

st.markdown(f"<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: MASTER COMMANDER v67.0</h1>", unsafe_allow_html=True)

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (Entry, SL, TG) ---
with col_st:
    st.header("📈 NSE STOCK")
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = yf.Ticker(asset_st).history(period="5d", interval="1m")
    
    if not df_st.empty and len(df_st) > 100:
        df_st['E9'] = ta.ema(df_st['Close'], length=9)
        df_st['E21'] = ta.ema(df_st['Close'], length=21)
        df_st['E200'] = ta.ema(df_st['Close'], length=200)
        ltp_st = df_st['Close'].iloc[-1]
        
        is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp_st > df_st['E200'].iloc[-1])
        is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp_st < df_st['E200'].iloc[-1])

        if is_call and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp_st
            st.session_state.st_sl = ltp_st - 45; st.session_state.st_tg = ltp_st + 100
            jarvis_speak(f"NSE Call Signal! Entry at {round(ltp_st)}. Target 100 points.")
        elif is_put and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp_st
            st.session_state.st_sl = ltp_st + 45; st.session_state.st_tg = ltp_st - 100
            jarvis_speak(f"NSE Put Signal! Entry at {round(ltp_st)}. Target 100 points.")

        st.metric(f"LIVE {asset_st}", f"₹{round(ltp_st,2)}", delta=st.session_state.st_last)
        st.success(f"**ENTRY:** {st.session_state.st_ep} | **SL:** {st.session_state.st_sl} | **TARGET:** {st.session_state.st_tg}")
        
        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO (Entry, SL, TG + Position Sizer) ---
with col_cr:
    st.header("₿ CRYPTO MARKET")
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        res = requests.get(url, timeout=3).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)
            df_cr['E200'] = ta.ema(df_cr['close'], length=200)
            ltp_cr = float(df_cr['close'].iloc[-1])

            if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_cr > df_cr['E200'].iloc[-1] and st.session_state.cr_last != "CALL":
                st.session_state.cr_last = "CALL"; st.session_state.cr_ep = ltp_cr
                st.session_state.cr_sl = ltp_cr - 200; st.session_state.cr_tg = ltp_cr + 500
                jarvis_speak("Crypto Call Buy! Target 500 dollars.")
            elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_cr < df_cr['E200'].iloc[-1] and st.session_state.cr_last != "PUT":
                st.session_state.cr_last = "PUT"; st.session_state.cr_ep = ltp_cr
                st.session_state.cr_sl = ltp_cr + 200; st.session_state.cr_tg = ltp_cr - 500
                jarvis_speak("Crypto Put Buy! Target 500 dollars.")

            st.metric("BTC PRICE", f"${ltp_cr}", delta=st.session_state.cr_last)
            
            # --- 🛡️ POSITION & LEVELS ---
            st.warning(f"💰 Balance: ${CAPITAL} | Qty: {round((CAPITAL*10)/ltp_cr, 4)} BTC")
            st.info(f"**ENTRY:** {st.session_state.cr_ep} | **SL:** {st.session_state.cr_sl} | **TARGET:** {st.session_state.cr_tg}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Crypto Syncing...")

if st.button("🔄 FULL SYSTEM RESET"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
