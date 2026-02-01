import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis R: Unbreakable", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v25_unbreakable")

# --- 🔊 2. VOICE ENGINE ---
def jarvis_r_speak(text, alert_type="normal"):
    js = f"""
    <script>
    window.speechSynthesis.cancel();
    var m = new SpeechSynthesisUtterance('{text}');
    m.lang = 'hi-IN'; m.rate = 1.0;
    window.speechSynthesis.speak(m);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🧠 3. LIGHTNING DATA ENGINE ---
def get_fast_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=150"
    try:
        response = requests.get(url).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return pd.DataFrame()

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛡️ JARVIS-R: UNBREAKABLE v25.0</h1>", unsafe_allow_html=True)

# State Management
if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""

# --- 🚀 4. EXECUTION ENGINE ---
df = get_fast_data()

# GUARD: Check if data is valid and has enough rows
if not df.empty and len(df) > 50:
    try:
        # Indicators
        df['EMA9'] = ta.ema(df['close'], length=9)
        df['EMA21'] = ta.ema(df['close'], length=21)
        df['EMA200'] = ta.ema(df['close'], length=200)
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['ADX'] = adx_df['ADX_14']
        
        ltp = float(df['close'].iloc[-1])
        cur_adx = float(df['ADX'].iloc[-1])

        # Logic
        is_buy = bool(df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and ltp > df['EMA200'].iloc[-1] and cur_adx > 20)
        is_sell = bool(df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and ltp < df['EMA200'].iloc[-1] and cur_adx > 20)

        # Signal Trigger
        if is_buy and st.session_state.l_s != "BUY":
            st.session_state.l_s = "BUY"
            st.session_state.e_p = ltp
            jarvis_r_speak(f"Master Buy Signal at {ltp}")
        elif is_sell and st.session_state.l_s != "SELL":
            st.session_state.l_s = "SELL"
            st.session_state.e_p = ltp
            jarvis_r_speak(f"Master Sell Signal at {ltp}")

        # PNL & Momentum Tracking
        if st.session_state.e_p > 0:
            diff = round(abs(ltp - st.session_state.e_p), 2)
            if diff >= 300:
                jarvis_r_speak("Rajveer Sir, bada momentum hai! Ruko nahi, trend strong hai!")
            
            # Reversal Exit
            rev = (st.session_state.l_s == "BUY" and ltp < df['EMA9'].iloc[-1]) or (st.session_state.l_s == "SELL" and ltp > df['EMA9'].iloc[-1])
            if rev and diff > 50:
                jarvis_r_speak("Exit! Trend palat raha hai.")
                st.session_state.e_p = 0.0
                st.session_state.l_s = "EXIT"

        # --- 📺 DISPLAY ---
        c1, c2, c3 = st.columns(3)
        c1.metric("LTP", f"${ltp}")
        c2.metric("ENTRY PRICE", f"${st.session_state.e_p if st.session_state.e_p > 0 else '---'}")
        pnl_val = round(ltp - st.session_state.e_p if st.session_state.l_s == "BUY" else st.session_state.e_p - ltp, 2) if st.session_state.e_p > 0 else 0
        c3.metric("LIVE PNL", f"{pnl_val} Pts")

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning("📡 Calculations recalculating... please wait.")
else:
    st.info("📡 Connecting to High-Speed Satellite Feed...")

if st.button("🔄 Manual Trade Reset"):
    st.session_state.e_p = 0.0
    st.session_state.l_s = ""
    st.rerun()
