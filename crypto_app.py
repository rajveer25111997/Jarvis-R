import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings
from datetime import datetime

# --- 🎯 1. SETTINGS ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS-R", layout="wide")

# --- 🧠 2. ULTRA-STABLE DATA ENGINE ---
def get_data_v2(symbol):
    for i in range(3): # 3 baar koshish karega
        try:
            df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                return df
        except:
            time.sleep(0.2)
    return None

# --- 🔍 3. UI BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #f7931a, #ff4b4b); padding:15px; border-radius:15px; margin-bottom:10px;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: STABLE VERSION</h1>
    </div>
""", unsafe_allow_html=True)

# Session States
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "in_pos" not in st.session_state: st.session_state.in_pos = False

with st.sidebar:
    st.header("⚙️ Settings")
    coin = st.selectbox("Select Asset:", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"])
    st.write("Voice Status: Active ✅")

live_box = st.empty()

# --- 🏗️ 4. EXECUTION ENGINE ---
@st.fragment(run_every=2) # Thoda slow taaki data miss na ho
def jarvis_execution(target_coin):
    df = get_data_v2(target_coin)
    
    if df is not None and len(df) > 30:
        ltp = round(df['Close'].iloc[-1], 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # Signal Logic
        buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
        exit_sig = st.session_state.in_pos and (df['E9'].iloc[-1] < df['E21'].iloc[-1])
        
        sig, col = ("⌛ SCANNING", "#555555")
        if buy_sig: sig, col = ("🚀 MASTER BUY", "#00ff00")
        elif st.session_state.in_pos: sig, col = ("💎 HOLDING", "#00ff00")

        # VOICE FIX: Alag alert box
        if buy_sig and not st.session_state.in_pos:
            st.session_state.in_pos = True
            st.toast(f"MASTER BUY ON {target_coin}!")
            st.components.v1.html(f"""<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg"></audio>
                <script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Rajveer Sir, Master Buy Alert'));</script>""", height=0)

        if exit_sig:
            st.session_state.in_pos = False
            st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Trend Reversed, Exit Now'));</script>", height=0)

        # RENDER DASHBOARD
        with live_box.container():
            st.markdown(f"<h1 style='text-align:center; color:{col};'>{sig} | ${ltp}</h1>", unsafe_allow_html=True)
            
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")

    else:
        st.warning("Jarvis-R: Waiting for Data Connection... 📡")

jarvis_execution(coin)
