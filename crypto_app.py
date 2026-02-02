import streamlit as st
import yfinance as yf
import requests
import pandas as pd 
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS DUAL: CALL-PUT MASTER", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v69_callput")

def jarvis_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. STATE MANAGEMENT ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_last": "", "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0,
        "cr_last": "", "cr_ep": 0.0, "cr_sl": 0.0, "cr_tg": 0.0,
        "balance": 120.0 
    })

st.markdown(f"<h1 style='text-align:center; color:#FFD700;'>🛡️ JARVIS DUAL: CALL & PUT COMMANDER v69.0</h1>", unsafe_allow_html=True)

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE CALL/PUT) ---
with col_st:
    st.header("📈 NSE STOCK")
    asset_st = st.sidebar.selectbox("Select NSE", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = yf.Ticker(asset_st).history(period="5d", interval="1m")
    
    if not df_st.empty and len(df_st) > 100:
        df_st['E9'] = ta.ema(df_st['Close'], length=9)
        df_st['E21'] = ta.ema(df_st['Close'], length=21)
        df_st['E200'] = ta.ema(df_st['Close'], length=200)
        ltp_st = df_st['Close'].iloc[-1]
        
        # --- 🚦 CALL/PUT LOGIC ---
        is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp_st > df_st['E200'].iloc[-1])
        is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp_st < df_st['E200'].iloc[-1])

        if is_call and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = round(ltp_st, 2)
            st.session_state.st_sl = round(ltp_st - 45, 2); st.session_state.st_tg = round(ltp_st + 100, 2)
            jarvis_speak(f"NSE Call Signal Locked!")
        elif is_put and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = round(ltp_st, 2)
            st.session_state.st_sl = round(ltp_st + 45, 2); st.session_state.st_tg = round(ltp_st - 100, 2)
            jarvis_speak(f"NSE Put Signal Locked!")

        st.metric(f"LIVE {asset_st}", f"₹{round(ltp_st,2)}", delta=st.session_state.st_last)
        st.success(f"📌 {st.session_state.st_last} LOCKED - Entry: {st.session_state.st_ep} | SL: {st.session_state.st_sl} | TG: {st.session_state.st_tg}")
        
        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO MARKET (BTC CALL/PUT) ---
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

            # --- 🚦 CALL/PUT LOGIC ---
            is_call_r = bool(df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_cr > df_cr['E200'].iloc[-1])
            is_put_r = bool(df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_cr < df_cr['E200'].iloc[-1])

            if is_call_r and st.session_state.cr_last != "CALL":
                st.session_state.cr_last = "CALL"; st.session_state.cr_ep = round(ltp_cr, 2)
                st.session_state.cr_sl = round(ltp_cr - 200, 2); st.session_state.cr_tg = round(ltp_cr + 500, 2)
                jarvis_speak("Crypto Call Buy!")
            elif is_put_r and st.session_state.cr_last != "PUT":
                st.session_state.cr_last = "PUT"; st.session_state.cr_ep = round(ltp_cr, 2)
                st.session_state.cr_sl = round(ltp_cr + 200, 2); st.session_state.cr_tg = round(ltp_cr - 500, 2)
                jarvis_speak("Crypto Put Buy!")

            st.metric("BTC PRICE", f"${ltp_cr}", delta=st.session_state.cr_last)
            
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Balance: ${st.session_state.balance} | Qty: {qty} BTC (10x)")
            st.info(f"📌 {st.session_state.cr_last} LOCKED - Entry: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl} | TG: {st.session_state.cr_tg}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Crypto Syncing...")

# --- 🛡️ THE MASTER BUTTON ---
st.write("---")
if st.button("🔄 FULL SYSTEM RESET & UNLOCK"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
