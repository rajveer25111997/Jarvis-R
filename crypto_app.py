import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis R: Command Center", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v29_final")

# --- 🔊 2. VOICE ENGINE ---
def jarvis_r_speak(text):
    js = f"""
    <script>
    window.speechSynthesis.cancel();
    var m = new SpeechSynthesisUtterance('{text}');
    m.lang = 'hi-IN'; m.rate = 1.0;
    window.speechSynthesis.speak(m);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🧠 3. DATA ENGINE ---
def get_fast_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        response = requests.get(url).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return pd.DataFrame()

# --- 🎨 4. BRANDING ---
st.markdown("<h1 style='text-align:center; color:#FFD700; font-size: 50px;'>🎯 JARVIS-R: VISUAL COMMAND CENTER</h1>", unsafe_allow_html=True)

if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""

# --- 🚀 5. EXECUTION ---
df = get_fast_data()

# Check if we have enough data
if not df.empty and len(df) > 200:
    try:
        # Calculations
        df['EMA9'] = ta.ema(df['close'], length=9)
        df['EMA21'] = ta.ema(df['close'], length=21)
        df['EMA200'] = ta.ema(df['close'], length=200)
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['ADX'] = adx_df['ADX_14']
        df.dropna(subset=['EMA200'], inplace=True)

        ltp = float(df['close'].iloc[-1])
        cur_adx = float(df['ADX'].iloc[-1])
        
        # Logic
        is_trending = cur_adx > 20
        is_call = bool(is_trending and df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and ltp > df['EMA200'].iloc[-1])
        is_put = bool(is_trending and df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and ltp < df['EMA200'].iloc[-1])

        # Voice Trigger
        if is_call and st.session_state.l_s != "CALL":
            st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
            jarvis_r_speak("Rajveer Sir, Call Option Buy karo!")
        elif is_put and st.session_state.l_s != "PUT":
            st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
            jarvis_r_speak("Rajveer Sir, Put Option Buy karo!")

        # --- 📺 VISUAL SIGNAL BOX ---
        if st.session_state.l_s == "CALL":
            st.markdown(f"""<div style='background-color:#1E5631; padding:30px; border-radius:15px; text-align:center; border: 5px solid #00FF00;'>
                <h1 style='color:white; font-size: 60px; margin:0;'>🚀 BUY CALL OPTION</h1>
                <h2 style='color:#FFD700; margin:10px;'>ENTRY: ${st.session_state.e_p} | LIVE: ${ltp}</h2>
            </div>""", unsafe_allow_html=True)
        elif st.session_state.l_s == "PUT":
            st.markdown(f"""<div style='background-color:#800000; padding:30px; border-radius:15px; text-align:center; border: 5px solid #FF0000;'>
                <h1 style='color:white; font-size: 60px; margin:0;'>📉 BUY PUT OPTION</h1>
                <h2 style='color:#FFD700; margin:10px;'>ENTRY: ${st.session_state.e_p} | LIVE: ${ltp}</h2>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#1B2631; padding:20px; border-radius:15px; text-align:center;'><h2>⌛ Scanning Markets for High-Probability Signal...</h2></div>", unsafe_allow_html=True)

        # --- 📊 METRICS & CHART ---
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("LIVE BITCOIN", f"${ltp}")
        m2.metric("TREND STRENGTH (ADX)", round(cur_adx, 2))
        pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2) if st.session_state.e_p > 0 else 0
        m3.metric("LIVE POINTS", f"{pnl} Pts", delta=pnl)

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange', width=2)))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.info("📡 Calculating Indicators... Please stay on the page.")
else:
    st.warning("📡 Waiting for sufficient market data to arrive (Need 200+ candles)...")

st.write("---")
if st.button("🔄 Reset Trade / Scan Next Signal"):
    st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()
