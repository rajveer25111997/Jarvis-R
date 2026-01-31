import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime

# --- 🎯 1. ULTIMATE CONFIGURATION ---
st.set_page_config(page_title="JARVIS-R: 43-POINT", layout="wide", initial_sidebar_state="collapsed")

# 1-Second No-Blink Refresh
st_autorefresh(interval=1000, key="jarvis_refresh")

# --- 🧠 2. SMART DATA ENGINE ---
def get_crypto_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. UI BRANDING & EMERGENCY SYSTEM ---
st.markdown("""
    <style>
    .reportview-container { background: #07090f; }
    .stMetric { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    .emergency-glow { border: 2px solid #ff4b4b; box-shadow: 0px 0px 20px #ff4b4b; }
    </style>
    <div style='text-align:center; background:linear-gradient(90deg, #f7931a, #ff4b4b); padding:10px; border-radius:15px; margin-bottom:10px;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: 43-POINT COMMAND CENTER</h1>
        <p style='color:white; margin:0; font-weight:bold;'>MASTER EDITION FOR RAJVEER SIR</p>
    </div>
""", unsafe_allow_html=True)

# Session States
if "pnl_history" not in st.session_state: st.session_state.pnl_history = []
if "entry_p" not in st.session_state: st.session_state.entry_p = 0.0
if "in_trade" not in st.session_state: st.session_state.in_trade = False

# --- ⚙️ 4. AUTOMATIC STRIKE & PORTFOLIO DOCTOR ---
with st.sidebar:
    st.header("🏥 Portfolio Doctor")
    capital = st.number_input("Starting Capital (₹):", value=5000)
    risk_per_trade = capital * 0.02
    st.info(f"Safe Risk: ₹{risk_per_trade} (2%)")
    
    st.divider()
    coin = st.selectbox("Select Asset:", ["BTC-USD", "ETH-USD", "SOL-USD"])
    
    # Auto Strike Logic
    st.subheader("🎯 Auto Strike Selection")
    st.write(f"Focusing on At-the-Money (ATM) for {coin}")

# --- 🏗️ 5. THE 43-POINT CORE LOGIC ---
df = get_crypto_data(coin)

if df is not None and len(df) > 30:
    ltp = round(float(df['Close'].iloc[-1]), 2)
    
    # 1-9: Javed Setup (EMA 9/21)
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # 10-15: Whale Radar (Volume Spike detection)
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    curr_vol = df['Volume'].iloc[-1]
    whale_detected = curr_vol > (avg_vol * 2.5)
    
    # 16-30: Entry/Exit Disciplines
    is_bullish = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    is_bearish = (df['E9'].iloc[-1] < df['E21'].iloc[-1])
    
    # --- 🚦 SIGNAL & SIREN ---
    sig, col, glow = "⌛ SCANNING", "#555555", ""
    
    if is_bullish and not st.session_state.in_trade:
        st.session_state.in_trade = True
        st.session_state.entry_p = ltp
        # Voice alert
        st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Rajveer Sir, Master Buy Entry Detected'));</script>", height=0)
    
    # 31-43: Karishma SL & Emergency Siren
    if st.session_state.in_trade:
        sl = round(st.session_state.entry_p * 0.99, 2)
        tgt = round(st.session_state.entry_p * 1.02, 2)
        
        if ltp <= sl or is_bearish:
            # EMERGENCY SIREN
            st.session_state.in_trade = False
            sig, col, glow = "🚨 EMERGENCY EXIT", "#ff4b4b", "emergency-glow"
            st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Emergency! Trend Reversed! Exit Now!'));</script>", height=0)
        elif ltp >= tgt:
            sig, col = "🎯 TARGET HIT", "#00ff00"
        else:
            sig, col = "💎 HOLDING", "#00ff00"

    # --- 📺 DISPLAY COMMAND CENTER ---
    c1, c2 = st.columns([3, 1])
    
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='EMA 9 (Javed)', line=dict(color='#00ff00', width=1)))
        fig.add_trace(go.Scatter(x=df.index, y=df['E21'], name='EMA 21 (Javed)', line=dict(color='#ff4b4b', width=1)))
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"""
            <div style='background:#111; padding:20px; border-radius:15px; border:2px solid {col}; text-align:center;'>
                <p style='color:gray; margin:0;'>LIVE PRICE</p>
                <h1 style='color:white; margin:0;'>${ltp}</h1>
                <h2 style='color:{col};'>{sig}</h2>
                <hr style='border-color:#333;'>
                <p style='color:{"#00ff00" if whale_detected else "gray"};'>WHALE RADAR: {"⚡ ACTIVE" if whale_detected else "IDLE"}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.metric("ENTRY", f"${st.session_state.entry_p if st.session_state.entry_p > 0 else '---'}")
        st.metric("KARISHMA SL (1%)", f"${round(st.session_state.entry_p*0.99, 2) if st.session_state.entry_p > 0 else '---'}", delta="-₹ Limit")
        st.metric("TARGET (2%)", f"${round(st.session_state.entry_p*1.02, 2) if st.session_state.entry_p > 0 else '---'}", delta="+₹ Gain")

else:
    st.error("📡 Connecting to Jarvis-R Satellite... Please wait.")

