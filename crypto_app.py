import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- 🎯 1. ULTRA-STABLE CONFIG ---
st.set_page_config(page_title="Jarvis R: Momentum Saver", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v34_momentum") # 1-Sec Tick

def jarvis_r_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. HYBRID DATA ENGINE (No-Reload Logic) ---
def get_crypto_data():
    # सीधे लाइव डेटा फेच करना बिना भारी लाइब्रेरी के
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        response = requests.get(url, timeout=2).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except:
        return None

st.markdown("<h1 style='text-align:center; color:#00FF00;'>⚡ JARVIS-R: MOMENTUM SAVER v34.0</h1>", unsafe_allow_html=True)

# Persistent States
if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""
if "last_df" not in st.session_state: st.session_state.last_df = pd.DataFrame()

# --- 🚀 3. THE EXECUTION ---
raw_data = get_crypto_data()

# अगर नया डेटा मिला तो अपडेट करें, वरना पुराने को ही दिखाएँ (Connecting नहीं आएगा)
if raw_data is not None:
    st.session_state.last_df = raw_data

df = st.session_state.last_df

if not df.empty and len(df) > 100:
    try:
        # Technicals
        df['EMA9'] = ta.ema(df['close'], length=9)
        df['EMA21'] = ta.ema(df['close'], length=21)
        df['EMA200'] = ta.ema(df['close'], length=200)
        
        ltp = float(df['close'].iloc[-1])
        ema9, ema21, ema200 = df['EMA9'].iloc[-1], df['EMA21'].iloc[-1], df['EMA200'].iloc[-1]

        # --- 🚦 MOMENTUM SIGNAL ---
        is_call = bool(ema9 > ema21 and ltp > ema200)
        is_put = bool(ema9 < ema21 and ltp < ema200)

        if is_call and st.session_state.l_s != "CALL":
            st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
            jarvis_r_speak(f"Rajveer Sir, Call Option Buy. Momentum fast hai!")
        elif is_put and st.session_state.l_s != "PUT":
            st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
            jarvis_r_speak(f"Rajveer Sir, Put Option Buy. Market dropping!")

        # --- 📺 PRO DASHBOARD ---
        c1, c2, c3 = st.columns(3)
        c1.metric("LIVE PRICE", f"${ltp}")
        c2.metric("SIGNAL", st.session_state.l_s if st.session_state.l_s else "WAITING")
        pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2) if st.session_state.e_p > 0 else 0
        c3.metric("PNL (POINTS)", f"{pnl} Pts", delta=pnl)

        # बड़ा कॉल/पुट बॉक्स
        if st.session_state.l_s != "":
            box_color = "#1E5631" if st.session_state.l_s == "CALL" else "#800000"
            st.markdown(f"<div style='background-color:{box_color}; padding:15px; border-radius:10px; text-align:center;'><h2>ACTIVE: {st.session_state.l_s} @ ${st.session_state.e_p}</h2></div>", unsafe_allow_html=True)

        # Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.write("Recalculating...")
else:
    st.warning("Connecting to Fast API... Please wait.")

if st.button("🔄 Reset Manual"):
    st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()
