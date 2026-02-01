import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta # इसके लिए 'pip install pandas_ta' ज़रूरी है
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis R: Anti-Fakeout", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v24_fix")

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

# --- 🧠 3. DATA ENGINE ---
def get_fast_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=150"
    try:
        response = requests.get(url).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return pd.DataFrame()

st.markdown("<h1 style='text-align:center; color:#FF4B4B;'>🛡️ JARVIS-R: ANTI-FAKE SIGNAL v24.0</h1>", unsafe_allow_html=True)

# State Management
if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""

# --- 🚀 4. EXECUTION & SMART FILTERS ---
df = get_fast_data()

if not df.empty:
    # --- 📊 Indicators Calculation ---
    df['EMA9'] = ta.ema(df['close'], length=9)
    df['EMA21'] = ta.ema(df['close'], length=21)
    df['EMA200'] = ta.ema(df['close'], length=200)
    # ADX: Trend Strength Filter (25 के ऊपर मतलब मजबूत ट्रेंड)
    adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
    df['ADX'] = adx_df['ADX_14']
    
    ltp = float(df['close'].iloc[-1])
    current_adx = df['ADX'].iloc[-1]

    # --- 🚦 SMART SIGNAL LOGIC (Filtering False Signals) ---
    # 1. Trend Strength Check (ADX > 25)
    # 2. EMA Crossover
    # 3. Price confirmation (Above/Below 200 EMA)
    
    is_trending = current_adx > 22 # Market में हलचल है
    
    buy_condition = (is_trending and 
                     df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and 
                     ltp > df['EMA200'].iloc[-1] and 
                     ltp > df['high'].iloc[-2]) # Price Confirmation

    sell_condition = (is_trending and 
                      df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and 
                      ltp < df['EMA200'].iloc[-1] and 
                      ltp < df['low'].iloc[-2]) # Price Confirmation

    # --- 🚨 SIGNAL TRIGGER ---
    if buy_condition and st.session_state.l_s != "BUY":
        st.session_state.l_s = "BUY"
        st.session_state.e_p = ltp
        jarvis_r_speak(f"Confirm Buy Signal at {ltp}. Trend is strong.")

    elif sell_condition and st.session_state.l_s != "SELL":
        st.session_state.l_s = "SELL"
        st.session_state.e_p = ltp
        jarvis_r_speak(f"Confirm Sell Signal at {ltp}. Momentum is crashing.")

    # --- 📺 DASHBOARD ---
    col1, col2, col3 = st.columns(3)
    col1.metric("LTP", f"${ltp}")
    col2.metric("ENTRY", f"${st.session_state.e_p}")
    # ADX Color Coding
    adx_color = "green" if current_adx > 25 else "red"
    col3.markdown(f"**Trend Strength (ADX):** <span style='color:{adx_color};'>{round(current_adx, 2)}</span>", unsafe_allow_html=True)

    if current_adx < 22:
        st.warning("⚠️ Market is Sideways. Jarvis is ignoring signals to save your capital.")

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'], name='EMA 9', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA21'], name='EMA 21', line=dict(color='yellow')))
    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

if st.button("🔄 Reset Trade"):
    st.session_state.e_p = 0.0
    st.session_state.l_s = ""
    st.rerun()
