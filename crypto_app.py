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
    <div style='text-align:center; background:linear-gradient(90deg, #f7931a, #ff4b4b); padding:15px; border-radius:15px; margin-bottom:10px;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: ULTIMATE EDITION</h1>
        <p style='color:white; margin:0; font-weight:bold;'>RAJVEER'S PROPRIETARY TRADING SYSTEM</p>
    </div>
""", unsafe_allow_html=True)

# Session States
if "history" not in st.session_state: st.session_state.history = []
if "entry_usd" not in st.session_state: st.session_state.entry_usd = 0.0
if "in_pos" not in st.session_state: st.session_state.in_pos = False
if "total_pnl" not in st.session_state: st.session_state.total_pnl = 0.0

# --- ⚙️ CONTROL CENTER (Fixed: Moved out of fragment) ---
coins = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
with st.sidebar:
    st.header("🎯 Target Selection")
    main_coin = st.selectbox("Select Target Focus:", coins)
    st.divider()
    st.metric("Total Daily PnL", f"${round(st.session_state.total_pnl, 2)}")

live_area = st.empty()

# --- 🏗️ 4. STABLE EXECUTION ENGINE ---
@st.fragment(run_every=1)
def jarvis_r_stable(target_coin):
    # Top Bar Prices
    top_cols = st.columns(len(coins))
    for i, c in enumerate(top_cols):
        data = get_data(coins[i])
        if data is not None:
            p = round(data['Close'].iloc[-1], 2)
            with c:
                st.markdown(f"<div style='background:#111; padding:10px; border-radius:10px; text-align:center;'><p style='color:gray; font-size:12px; margin:0;'>{coins[i]}</p><h4 style='color:white; margin:0;'>${p}</h4></div>", unsafe_allow_html=True)

    st.divider()
    
    df = get_data(target_coin)
    if df is not None and len(df) > 20:
        ltp = round(df['Close'].iloc[-1], 2)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # Whale Radar & Logic
        is_whale = df['Volume'].iloc[-1] > (df['Volume'].rolling(20).mean().iloc[-1] * 2)
        buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
        exit_sig = st.session_state.in_pos and (df['E9'].iloc[-1] < df['E21'].iloc[-1])
        
        sig, col, msg = ("⌛ SCANNING", "#555555", "Watching")
        if st.session_state.in_pos: sig, col, msg = ("💎 HOLDING", "#00ff00", "Trend is Strong")

        # Voice & State Updates
        if buy_sig and not st.session_state.in_pos:
            st.session_state.in_pos, st.session_state.entry_usd = True, ltp
            st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Rajveer Sir, Master Buy on {target_coin}'));</script>", height=0)
        
        if exit_sig:
            pnl = round(ltp - st.session_state.entry_usd, 2)
            st.session_state.total_pnl += pnl
            st.session_state.history.append({"coin": target_coin, "pnl": pnl, "time": datetime.now().strftime("%H:%M")})
            st.session_state.in_pos = False
            st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Trend Reversed, Exit Now'));</script>", height=0)

        # Dashboard UI
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True, key=f"ch_{time.time()}")
        with c2:
            st.markdown(f"""<div style='background:#111; padding:20px; border-radius:15px; border:2px solid {col}; text-align:center;'>
                <h2 style='color:white; margin:0;'>${ltp}</h2>
                <h3 style='color:{col};'>{sig}</h3>
                <p style='color:gray;'>WHALE: {'⚡ YES' if is_whale else 'NO'}</p>
                <hr>
                <p style='color:gray; margin:0;'>ENTRY: ${st.session_state.entry_usd if st.session_state.entry_usd > 0 else '---'}</p>
                <p style='color:{col};'>{msg}</p>
            </div>""", unsafe_allow_html=True)

        if st.session_state.history:
            st.write("### 📜 Recent Trades")
            for t in st.session_state.history[-3:]:
                st.info(f"{t['time']} | {t['coin']} | PnL: +${t['pnl']}")

# 🚀 Run
jarvis_r_stable(main_coin)
