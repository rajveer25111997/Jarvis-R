import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. STABLE CONFIG ---
st.set_page_config(page_title="Jarvis R: Anti-Flicker", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v33_stable") # 2 Seconds for better stability

def jarvis_r_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. DATA MEMORY ENGINE ---
@st.cache_data(ttl=1) # 1 सेकंड के लिए डेटा को मेमोरी में रखेगा
def get_stable_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=500"
    try:
        response = requests.get(url, timeout=3).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except:
        return None # अगर एरर आए तो None भेजें

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛡️ JARVIS-R: ANTI-FLICKER v33.0</h1>", unsafe_allow_html=True)

# State Management
if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""
if "cached_df" not in st.session_state: st.session_state.cached_df = pd.DataFrame()

# --- 🚀 3. THE ENGINE ---
new_data = get_stable_data()

# अगर नया डेटा नहीं मिला, तो पुराना (cached) डेटा इस्तेमाल करें
if new_data is not None:
    st.session_state.cached_df = new_data

df = st.session_state.cached_df

if not df.empty and len(df) > 200:
    try:
        # Technicals
        df['EMA9'] = ta.ema(df['close'], length=9)
        df['EMA21'] = ta.ema(df['close'], length=21)
        df['EMA200'] = ta.ema(df['close'], length=200)
        
        ltp = float(df['close'].iloc[-1])
        
        # --- 🚦 SIGNAL LOGIC ---
        is_call = bool(df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and ltp > df['EMA200'].iloc[-1])
        is_put = bool(df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and ltp < df['EMA200'].iloc[-1])

        if is_call and st.session_state.l_s != "CALL":
            st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
            jarvis_r_speak("Rajveer Sir, Call Buy Karo")
        elif is_put and st.session_state.l_s != "PUT":
            st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
            jarvis_r_speak("Rajveer Sir, Put Buy Karo")

        # --- 📺 ALWAYS-ON DASHBOARD ---
        c1, c2, c3 = st.columns(3)
        c1.metric("LIVE BTC", f"${ltp}")
        c2.metric("ENTRY", f"${st.session_state.e_p if st.session_state.e_p > 0 else '---'}")
        pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2) if st.session_state.e_p > 0 else 0
        c3.metric("PNL POINTS", f"{pnl} Pts")

        # Big Display for Signal
        if st.session_state.l_s != "":
            color = "#1E5631" if st.session_state.l_s == "CALL" else "#800000"
            st.success(f"ACTIVE: {st.session_state.l_s}")

        # Always Show Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.info("🔄 Optimizing data feed...")
else:
    st.warning("📡 Initializing Satellite Connection... Please wait 5 seconds.")

if st.button("🔄 Reset Trade"):
    st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()
