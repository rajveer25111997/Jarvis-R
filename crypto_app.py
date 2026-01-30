import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

# --- 🎯 1. SETTINGS ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS-R", layout="wide")

# --- 🧠 2. DATA ENGINE ---
def get_crypto_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. UI BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #f7931a, #ff4b4b); padding:15px; border-radius:15px; margin-bottom:20px;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R (Rajveer Edition)</h1>
        <p style='color:white; margin:0; font-weight:bold;'>CRYPTO PREDICTOR | 24/7 GLOBAL SCANNER</p>
    </div>
""", unsafe_allow_html=True)

# Session States
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry_usd" not in st.session_state: st.session_state.entry_usd = 0.0

# --- ⚙️ CONTROL CENTER (Fixed: Moved outside fragment) ---
with st.sidebar:
    st.header("⚙️ Sniper Setup")
    coin_choice = st.selectbox("Select Coin:", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"])

live_area = st.empty()

# --- 🏗️ 4. STABLE EXECUTION ENGINE ---
@st.fragment(run_every=1)
def jarvis_r_engine(coin):
    df = get_crypto_data(coin)
    
    if df is not None and len(df) > 20:
        price = round(float(df['Close'].iloc[-1]), 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # Signal Logic
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (price > df['E200'].iloc[-1])
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (price < df['E200'].iloc[-1])
        
        if is_buy: sig, col = "🚀 MASTER BUY", "#00ff00"
        elif is_sell: sig, col = "📉 MASTER SELL", "#ff4b4b"
        else: sig, col = "⌛ SCANNING...", "#555555"

        # Voice Alert
        if "MASTER" in sig and st.session_state.last_sig != sig:
            st.session_state.last_sig = sig
            st.session_state.entry_usd = price
            voice = f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Rajveer Sir, {sig} on {coin} at {price} dollars.'));</script>"
            st.components.v1.html(voice, height=0)

        with live_area.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=420, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #f7931a; text-align:center; height:420px; display:flex; flex-direction:column; justify-content:center;">
                        <h4 style="color:gray;">{coin} PRICE</h4>
                        <h1 style="color:#f7931a; font-size:50px;">${price}</h1>
                        <h2 style="color:{col};">{sig}</h2>
                        <hr style="border-color:#333;">
                        <p style="color:white;">ENTRY: ${st.session_state.entry_usd if st.session_state.entry_usd > 0 else '---'}</p>
                    </div>
                """, unsafe_allow_html=True)

# 🚀 Launch
jarvis_r_engine(coin_choice)
