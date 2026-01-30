import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings
from datetime import datetime

# --- 🎯 1. CORE SETTINGS ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS-R ULTIMATE", layout="wide")

# --- 🧠 2. LIVE DATA ENGINE (High Speed Fix) ---
def get_live_data(symbol):
    try:
        # Live Bhav ke liye '1d' period aur '1m' interval sabse fast hai
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except Exception as e:
        return None
    return None

# --- 🔍 3. UI BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #f7931a, #ff4b4b); padding:15px; border-radius:15px; margin-bottom:10px;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: COMMAND CENTER</h1>
        <p style='color:white; margin:0;'>LIVE PRICE | TARGET | EXIT | VOICE ACTIVE</p>
    </div>
""", unsafe_allow_html=True)

# Session States for Levels
if "entry_usd" not in st.session_state: st.session_state.entry_usd = 0.0
if "in_pos" not in st.session_state: st.session_state.in_pos = False

with st.sidebar:
    st.header("⚙️ Sniper Control")
    coin = st.selectbox("Select Asset:", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"])
    st.info("Tip: Browser ki settings mein 'Autoplay Sound' allow karein.")

live_dashboard = st.empty()

# --- 🏗️ 4. EXECUTION ENGINE ---
@st.fragment(run_every=1)
def jarvis_execution(target_coin):
    df = get_live_data(target_coin)
    
    if df is not None and len(df) > 20:
        ltp = round(float(df['Close'].iloc[-1]), 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # 🎯 Logic
        buy_cond = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
        exit_cond = st.session_state.in_pos and (df['E9'].iloc[-1] < df['E21'].iloc[-1])
        
        sig, col = ("⌛ SCANNING", "#555555")
        
        # --- VOICE & SIGNAL SYSTEM ---
        if buy_cond and not st.session_state.in_pos:
            st.session_state.in_pos = True
            st.session_state.entry_usd = ltp
            # Voice Alert
            st.components.v1.html(f"""
                <script>
                var msg = new SpeechSynthesisUtterance('Rajveer Sir, Master Buy on {target_coin} at {ltp}');
                window.speechSynthesis.speak(msg);
                </script>
            """, height=0)
        
        if exit_cond:
            st.session_state.in_pos = False
            st.components.v1.html(f"""
                <script>
                var msg = new SpeechSynthesisUtterance('Trend Reversed, Rajveer Sir Exit Now');
                window.speechSynthesis.speak(msg);
                </script>
            """, height=0)

        if st.session_state.in_pos: sig, col = ("🚀 HOLDING", "#00ff00")
        elif buy_cond: sig, col = ("🎯 BUY NOW", "#00ff00")

        # --- DASHBOARD UI ---
        with live_dashboard.container():
            # Live Bhav & Signal
            st.markdown(f"""
                <div style='background:#111; padding:20px; border-radius:15px; border:2px solid {col}; text-align:center;'>
                    <h4 style='color:gray; margin:0;'>LIVE PRICE</h4>
                    <h1 style='color:white; font-size:55px; margin:0;'>${ltp}</h1>
                    <h2 style='color:{col}; margin:0;'>{sig}</h2>
                </div>
            """, unsafe_allow_html=True)

            # Target & SL Box
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("ENTRY", f"${st.session_state.entry_usd if st.session_state.entry_usd > 0 else '---'}")
            with c2:
                tgt = round(st.session_state.entry_usd * 1.02, 2) if st.session_state.entry_usd > 0 else 0
                st.metric("TARGET (+2%)", f"${tgt if tgt > 0 else '---'}", delta="Profit")
            with c3:
                sl = round(st.session_state.entry_usd * 0.99, 2) if st.session_state.entry_usd > 0 else 0
                st.metric("KARISHMA SL (-1%)", f"${sl if sl > 0 else '---'}", delta="-Loss", delta_color="inverse")

            # Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")
    else:
        st.error("📡 Live Bhav Connection Error... Reconnecting")

# 🚀 Execute
jarvis_execution(coin)
