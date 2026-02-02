import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="Jarvis: Mega Hunter v72", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v72_mega")

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

st.markdown(f"<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS DUAL: MEGA-TREND HUNTER v72.0</h1>", unsafe_allow_html=True)

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE) ---
with col_st:
    st.header("📈 NSE MEGA-TREND")
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = yf.Ticker(asset_st).history(period="5d", interval="1m")
    
    if not df_st.empty and len(df_st) > 100:
        df_st['E9'] = ta.ema(df_st['Close'], length=9)
        df_st['E21'] = ta.ema(df_st['Close'], length=21)
        df_st['E200'] = ta.ema(df_st['Close'], length=200)
        # News/Volatility Filter
        df_st['ATR'] = ta.atr(df_st['High'], df_st['Low'], df_st['Close'], length=14)
        ltp_st = df_st['Close'].iloc[-1]
        atr_st = df_st['ATR'].iloc[-1]

        # MEGA SIGNAL LOGIC (Only Strong Trends)
        volatility_high = atr_st > df_st['ATR'].mean() # न्यूज़ के समय ATR बढ़ जाता है
        is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp_st > df_st['E200'].iloc[-1] and volatility_high)
        is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp_st < df_st['E200'].iloc[-1] and volatility_high)

        curr_sig = "CALL" if is_call else ("PUT" if is_put else "WAIT")

        if curr_sig != "WAIT" and curr_sig != st.session_state.st_last:
            st.session_state.st_last = curr_sig
            st.session_state.st_ep = round(ltp_st, 2)
            # Big Targets for Big Moves
            st.session_state.st_sl = round(ltp_st - 60, 2) if curr_sig == "CALL" else round(ltp_st + 60, 2)
            st.session_state.st_tg = round(ltp_st + 250, 2) if curr_sig == "CALL" else round(ltp_st - 250, 2)
            jarvis_speak(f"Rajveer Sir, High Impact News Signal! NSE {curr_sig} Locked for 250 points.")

        st.metric(f"LIVE {asset_st}", f"₹{round(ltp_st,2)}", delta="STRONG TREND" if volatility_high else "SIDEWAYS")
        st.success(f"📌 {st.session_state.st_last} - E: {st.session_state.st_ep} | SL: {st.session_state.st_sl} | TG: {st.session_state.st_tg}")
        
        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO (Bitcoin 500 Point Hunter) ---
with col_cr:
    st.header("₿ CRYPTO 500+ HUNTER")
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        res = requests.get(url, timeout=3).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)
            # Crypto ATR for News Detection
            df_cr['ATR'] = ta.atr(df_cr['high'], df_cr['low'], df_cr['close'], length=14)
            ltp_cr = float(df_cr['close'].iloc[-1])
            atr_cr = df_cr['ATR'].iloc[-1]

            # CRYPTO MEGA LOGIC
            cr_vol_high = atr_cr > df_cr['ATR'].tail(50).mean()
            is_call_r = bool(df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and cr_vol_high)
            is_put_r = bool(df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and cr_vol_high)

            cr_sig = "CALL" if is_call_r else ("PUT" if is_put_r else "WAIT")

            if cr_sig != "WAIT" and cr_sig != st.session_state.cr_last:
                st.session_state.cr_last = cr_sig
                st.session_state.cr_ep = round(ltp_cr, 2)
                st.session_state.cr_sl = round(ltp_cr - 250, 2) if cr_sig == "CALL" else round(ltp_cr + 250, 2)
                st.session_state.cr_tg = round(ltp_cr + 600, 2) if cr_sig == "CALL" else round(ltp_cr - 600, 2)
                jarvis_speak("Mega Crypto Trend Locked! 600 point target ready.")

            st.metric("BTC PRICE", f"${ltp_cr}", delta="NEWS IMPACT" if cr_vol_high else "CALM")
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Bal: ${st.session_state.balance} | Qty: {qty} BTC")
            st.info(f"📌 {st.session_state.cr_last} - E: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl} | TG: {st.session_state.cr_tg}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Crypto Syncing...")

if st.button("🔄 CLEAR & SCAN FOR NEXT MEGA TREND"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
