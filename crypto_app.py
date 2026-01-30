import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

# --- 🎯 1. JARVIS-R CORE SETTINGS ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="JARVIS-R ULTIMATE", layout="wide", initial_sidebar_state="collapsed")

# --- 🧠 2. DATA ENGINE (High Speed) ---
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

# --- 🏗️ 4. DASHBOARD FRAGMENT ---
live_area = st.empty()

@st.fragment(run_every=1)
def jarvis_r_final():
    # 🔥 MOST TRADED COINS LIST
    coins = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
    
    with live_area.container():
        # --- TOP BAR: MOST TRADED COINS ---
        cols = st.columns(len(coins))
        active_coin = coins[0] # Default
        
        for i, c in enumerate(cols):
            data = get_data(coins[i])
            if data is not None:
                p = round(data['Close'].iloc[-1], 2)
                change = round(((p - data['Open'].iloc[0]) / data['Open'].iloc[0]) * 100, 2)
                color = "#00ff00" if change >= 0 else "#ff4b4b"
                with c:
                    st.markdown(f"""<div style='background:#111; padding:10px; border-radius:10px; border-bottom:3px solid {color}; text-align:center;'>
                        <p style='color:gray; font-size:12px; margin:0;'>{coins[i]}</p>
                        <h3 style='color:white; margin:0;'>${p}</h3>
                        <p style='color:{color}; font-size:12px; margin:0;'>{change}%</p>
                    </div>""", unsafe_allow_html=True)

        st.divider()
        
        # --- MAIN ANALYSIS (Using first coin or selector) ---
        main_coin = st.selectbox("🎯 Target focus:", coins)
        df = get_data(main_coin)
        
        if df is not None and len(df) > 20:
            ltp = round(df['Close'].iloc[-1], 2)
            df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
            df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
            
            # Whale Radar (Volume)
            is_whale = df['Volume'].iloc[-1] > (df['Volume'].rolling(20).mean().iloc[-1] * 2)
            
            # Master Signal
            buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
            exit_sig = st.session_state.in_pos and (df['E9'].iloc[-1] < df['E21'].iloc[-1])
            
            sig, col, msg = ("💎 HOLDING", "#00ff00", "Stay in Trade") if st.session_state.in_pos else ("⌛ SCANNING", "#555555", "Watching Market")
            
            if buy_sig and not st.session_state.in_pos:
                st.session_state.in_pos, st.session_state.entry_usd = True, ltp
                sig, col = "🚀 MASTER BUY", "#00ff00"
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Master Buy on {main_coin}'));</script>", height=0)
            
            if exit_sig:
                profit = round(ltp - st.session_state.entry_usd, 2)
                st.session_state.history.append({"coin": main_coin, "pnl": profit, "time": datetime.now().strftime("%H:%M")})
                st.session_state.in_pos = False
                sig, col, msg = "🚨 EXIT NOW!", "#ff4b4b", f"Profit Booked: ${profit}"
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Exit Now, Profit Secured'));</script>", height=0)

            # --- RENDER DASHBOARD ---
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")
            
            with c2:
                st.markdown(f"""<div style='background:#111; padding:20px; border-radius:15px; border:1px solid {col}; text-align:center;'>
                    <h3 style='color:gray;'>{main_coin}</h3>
                    <h1 style='color:white;'>${ltp}</h1>
                    <h2 style='color:{col};'>{sig}</h2>
                    <p style='color:#00ff00;'>WHALE: {'⚡ YES' if is_whale else 'NO'}</p>
                    <hr>
                    <p style='color:gray;'>ENTRY: ${st.session_state.entry_usd if st.session_state.entry_usd > 0 else '---'}</p>
                    <p style='color:{col}; font-weight:bold;'>{msg}</p>
                </div>""", unsafe_allow_html=True)
                
        # --- TRADE HISTORY ---
        if st.session_state.history:
            st.write("### 📜 Recent Trades")
            h_cols = st.columns(min(len(st.session_state.history), 5))
            for i, trade in enumerate(st.session_state.history[-5:]):
                with h_cols[i]:
                    st.success(f"{trade['coin']}\n+${trade['pnl']}")

from datetime import datetime
jarvis_r_final()
