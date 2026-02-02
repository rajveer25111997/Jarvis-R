import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS DUAL: FINAL", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v65_final")

# --- 🔊 2. ULTIMATE VOICE & SIREN ---
def jarvis_speak_supreme(text):
    js_code = f"""
    <script>
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.lang = 'hi-IN';
    window.speechSynthesis.speak(msg);
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen'); }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: FINAL COMMAND CENTER v65.0</h1>", unsafe_allow_html=True)

# --- 🧠 3. STATE MANAGEMENT ---
if "st_last" not in st.session_state:
    st.session_state.update({
        "st_last": "", "st_ep": 0.0, "st_sl": 0.0,
        "r_last": "", "r_ep": 0.0, "r_sl": 0.0
    })

# --- 🚀 4. DUAL SCREEN LAYOUT ---
col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE) ---
with col_st:
    st.header("📈 NSE STOCK MARKET")
    asset_st = st.sidebar.selectbox("Select NSE Asset", ["^NSEI", "^NSEBANK", "SBIN.NS", "RELIANCE.NS"], key="st_box")
    
    try:
        # Ticker method is more stable during high volatility
        ticker = yf.Ticker(asset_st)
        df_st = ticker.history(period="5d", interval="1m")
        
        if not df_st.empty and len(df_st) > 100:
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            df_st['E200'] = ta.ema(df_st['Close'], length=200)
            ltp_st = float(df_st['Close'].iloc[-1])
            
            # Javed Strategy Logic
            is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp_st > df_st['E200'].iloc[-1])
            is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp_st < df_st['E200'].iloc[-1])

            if is_call and st.session_state.st_last != "CALL":
                st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp_st; st.session_state.st_sl = ltp_st - 40
                jarvis_speak_supreme(f"NSE Alert! {asset_st} Call Entry. Price {round(ltp_st,2)}")
            elif is_put and st.session_state.st_last != "PUT":
                st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp_st; st.session_state.st_sl = ltp_st + 40
                jarvis_speak_supreme(f"NSE Alert! {asset_st} Put Entry. Price {round(ltp_st,2)}")

            # Display NSE Dashboard
            st.metric(f"LIVE {asset_st}", f"₹{round(ltp_st,2)}", delta=st.session_state.st_last)
            st.success(f"**ENTRY:** {st.session_state.st_ep} | **SL:** {st.session_state.st_sl} | **STRIKE:** {round(ltp_st/100)*100}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.add_trace(go.Scatter(x=df_st.index, y=df_st['E200'], name='200 EMA', line=dict(color='orange')))
            fig_st.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_st, use_container_width=True)
        else:
            st.error("📡 NSE डेटा उपलब्ध नहीं है। कृपया इंटरनेट चेक करें।")
    except Exception as e:
        st.info("📡 NSE डेटा सिंक हो रहा है...")

# --- ₿ SECTION B: CRYPTO MARKET (Jarvis R) ---
with col_cr:
    st.header("₿ CRYPTO MARKET")
    try:
        url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
        res = requests.get(url, timeout=3).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)
            df_cr['E200'] = ta.ema(df_cr['close'], length=200)
            ltp_cr = float(df_cr['close'].iloc[-1])

            if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_cr > df_cr['E200'].iloc[-1] and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_cr; st.session_state.r_sl = ltp_cr - 150
                jarvis_speak_supreme("Crypto Call Buy!")
            elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_cr < df_cr['E200'].iloc[-1] and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_cr; st.session_state.r_sl = ltp_cr + 150
                jarvis_speak_supreme("Crypto Put Buy!")

            st.metric("BTC PRICE", f"${ltp_cr}", delta=st.session_state.r_last)
            st.warning(f"**ENTRY:** {st.session_state.r_ep} | **SL:** {st.session_state.r_sl}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except:
        st.info("📡 क्रिप्टो डेटा सिंक हो रहा है...")

# --- 🛡️ FULL RESET ---
if st.button("🔄 Full Reset Master System"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
