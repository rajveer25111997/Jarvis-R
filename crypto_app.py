import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings
from datetime import datetime

# --- 🎯 1. SETTINGS ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS-R ULTIMATE", layout="wide")

# --- 🧠 2. DATA ENGINE ---
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. UI BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #f7931a, #ff4b4b); padding:15px; border-radius:15px; margin-bottom:10px; box-shadow: 0px 4px 15px rgba(247, 147, 26, 0.4);'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: ULTIMATE</h1>
        <p style='color:white; margin:0; font-weight:bold;'>RAJVEER SIR'S TRADING COMMAND CENTER</p>
    </div>
""", unsafe_allow_html=True)

# Session States
if "history" not in st.session_state: st.session_state.history = []
if "entry_usd" not in st.session_state: st.session_state.entry_usd = 0.0
if "in_pos" not in st.session_state: st.session_state.in_pos = False
if "total_pnl" not in st.session_state: st.session_state.total_pnl = 0.0

# --- ⚙️ SIDEBAR CONTROL ---
coins = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
with st.sidebar:
    st.header("🎯 Focus Target")
    main_coin = st.selectbox("Select Asset:", coins)
    st.divider()
    st.metric("Total Daily Profit", f"${round(st.session_state.total_pnl, 2)}", delta=f"{len(st.session_state.history)} Trades")

live_area = st.empty()

# --- 🏗️ 4. EXECUTION ENGINE ---
@st.fragment(run_every=1)
def jarvis_r_engine(target_coin):
    df = get_data(target_coin)
    if df is not None and len(df) > 30:
        ltp = round(df['Close'].iloc[-1], 2)
        
        # INDICATORS
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        current_rsi = round(df['RSI'].iloc[-1], 2)

        # 🎯 SIGNAL LOGIC
        buy_cond = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
        exit_cond = st.session_state.in_pos and (df['E9'].iloc[-1] < df['E21'].iloc[-1])
        
        sig, col, shadow = ("⌛ SCANNING", "#555555", "0px 0px 0px")
        
        if buy_cond:
            sig, col, shadow = ("🚀 MASTER BUY", "#00ff00", "0px 0px 25px #00ff00")
            if not st.session_state.in_pos:
                st.session_state.in_pos, st.session_state.entry_usd = True, ltp
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Rajveer Sir, Master Buy on {target_coin}'));</script>", height=0)

        elif st.session_state.in_pos:
            sig, col, shadow = ("💎 HOLDING", "#00ff00", "0px 0px 15px #00ff00")
            if exit_cond:
                pnl = round(ltp - st.session_state.entry_usd, 2)
                st.session_state.total_pnl += pnl
                st.session_state.history.append({"coin": target_coin, "pnl": pnl, "time": datetime.now().strftime("%H:%M")})
                st.session_state.in_pos = False
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Exit Now, Profit Booked'));</script>", height=0)

        # --- DASHBOARD RENDER ---
        with live_area.container():
            # Signal Glow Box
            st.markdown(f"""
                <div style='background:#07090f; padding:20px; border-radius:20px; border:3px solid {col}; text-align:center; box-shadow: {shadow}; margin-bottom:20px;'>
                    <h1 style='color:{col}; margin:0; font-size:50px;'>{sig}</h1>
                    <p style='color:white; margin:0;'>Current Price: ${ltp} | RSI: {current_rsi}</p>
                </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
            with c2:
                st.markdown(f"""<div style='background:#111; padding:20px; border-radius:15px; border:1px solid #333; text-align:center;'>
                    <h4 style='color:gray;'>LIVE STATS</h4>
                    <p style='color:white;'>ENTRY: ${st.session_state.entry_usd if st.session_state.entry_usd > 0 else '---'}</p>
                    <p style='color:#00ff00;'>TARGET: ${round(st.session_state.entry_usd * 1.02, 2) if st.session_state.entry_usd > 0 else '---'}</p>
                    <p style='color:#ff4b4b;'>SL: ${round(st.session_state.entry_usd * 0.99, 2) if st.session_state.entry_usd > 0 else '---'}</p>
                </div>""", unsafe_allow_html=True)

            if st.session_state.history:
                st.write("### 📜 Recent Trades")
                cols = st.columns(3)
                for i, t in enumerate(st.session_state.history[-3:]):
                    with cols[i]: st.success(f"{t['coin']}: +${t['pnl']}")

# 🚀 Launch
jarvis_r_engine(main_coin)
