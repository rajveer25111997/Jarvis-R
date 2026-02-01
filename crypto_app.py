import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. PRO CONFIG ---
st.set_page_config(page_title="Jarvis R: Pro Station", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v30_pro")

# --- 🔊 2. VOICE ENGINE ---
def jarvis_r_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang = 'hi-IN'; m.rate = 1.0; window.speechSynthesis.speak(m);</script>"
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

# --- 🎨 4. INTERFACE ---
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛡️ JARVIS-R: PRO-TRADER STATION</h1>", unsafe_allow_html=True)

if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""

df = get_fast_data()

# --- 🚀 5. ALWAYS-ON DISPLAY ---
if not df.empty:
    # Basic Calculations
    ltp = float(df['close'].iloc[-1])
    day_high = df['high'].max()
    day_low = df['low'].min()
    
    # Technicals for Signals
    df['EMA9'] = ta.ema(df['close'], length=9)
    df['EMA21'] = ta.ema(df['close'], length=21)
    df['EMA200'] = ta.ema(df['close'], length=200)
    adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
    cur_adx = float(adx_df['ADX_14'].iloc[-1]) if adx_df is not None else 0

    # --- 🚦 SIGNAL LOGIC ---
    is_call = bool(cur_adx > 20 and df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and ltp > df['EMA200'].iloc[-1])
    is_put = bool(cur_adx > 20 and df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and ltp < df['EMA200'].iloc[-1])

    if is_call and st.session_state.l_s != "CALL":
        st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
        jarvis_r_speak("Rajveer Sir, Call entry detected!")
    elif is_put and st.session_state.l_s != "PUT":
        st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
        jarvis_r_speak("Rajveer Sir, Put entry detected!")

    # --- 📺 1. TOP BOX: LIVE SIGNAL ALERT ---
    if st.session_state.l_s != "":
        color = "#1E5631" if st.session_state.l_s == "CALL" else "#800000"
        border = "#00FF00" if st.session_state.l_s == "CALL" else "#FF0000"
        st.markdown(f"""<div style='background-color:{color}; padding:20px; border-radius:15px; text-align:center; border: 4px solid {border};'>
            <h1 style='color:white; margin:0;'>ACTIVE SIGNAL: {st.session_state.l_s}</h1>
            <h3 style='color:yellow; margin:5px;'>ENTRY: ${st.session_state.e_p} | LIVE: ${ltp}</h3>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color:#1B2631; padding:15px; border-radius:15px; text-align:center;'><h3>⌛ Scanning for Professional Entry...</h3></div>", unsafe_allow_html=True)

    st.write("---")

    # --- 📊 2. METRICS ROW ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("LIVE PRICE", f"${ltp}")
    c2.metric("24h HIGH", f"${day_high}")
    c3.metric("24h LOW", f"${day_low}")
    # Sentiment Logic
    sentiment = "BULLISH" if ltp > df['EMA200'].iloc[-1] else "BEARISH"
    c4.metric("SENTIMENT", sentiment)

    # --- 📈 3. MAIN CHART ---
    st.write("### 📺 Market Live View")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange', width=2)))
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # --- 🛡️ 4. TRADER'S PANEL ---
    st.write("---")
    tc1, tc2 = st.columns(2)
    with tc1:
        st.subheader("📋 Position Info")
        if st.session_state.e_p > 0:
            pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2)
            st.info(f"Entry: ${st.session_state.e_p} | Current PNL: {pnl} Pts")
        else:
            st.write("No active trade.")

    with tc2:
        st.subheader("⚙️ Control")
        if st.button("🔄 Reset Trade & Clear Alert"):
            st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()

else:
    st.warning("📡 Satellite data connecting... Please wait.")
