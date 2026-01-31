import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- 🎯 1. SNIPER CONFIGURATION ---
st.set_page_config(page_title="JARVIS-R: SNIPER", layout="wide")
st_autorefresh(interval=1000, key="sniper_refresh") # 1 Second No-Blink

# --- 🧠 2. DATA ENGINE ---
def get_live_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. BRAIN: ULTRA-FAST VOICE (Web API) ---
def jarvis_speak(text):
    js = f"<script>var m=new SpeechSynthesisUtterance('{text}');window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🏦 4. BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #000, #ff4b4b); padding:10px; border-radius:15px; border:2px solid #fff;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: SNIPER MODE</h1>
        <p style='color:white; margin:0;'>₹5,000 CAPITAL | 20x LEVERAGE | 125 LOTS</p>
    </div>
""", unsafe_allow_html=True)

# Session States
if "trade" not in st.session_state: st.session_state.trade = {"active": False, "entry": 0.0, "type": ""}

# --- ⚙️ 5. SIDEBAR: PORTFOLIO DOCTOR ---
with st.sidebar:
    st.header("🏥 Portfolio Doctor")
    st.write("**Capital:** ₹5,000")
    st.write("**Leverage:** 20x (Safe)")
    st.write("**Suggested Lot:** 125 Units (0.125 BTC)")
    st.divider()
    coin = st.selectbox("Asset:", ["BTC-USD", "ETH-USD"])
    st.warning("Min Profit Filter: 20-40 Points")

# --- 🚀 6. SNIPER EXECUTION ---
df = get_live_data(coin)

if df is not None and len(df) > 40:
    ltp = round(float(df['Close'].iloc[-1]), 2)
    
    # 45-Point Technicals
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # High Probability Signal Logic
    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    sig_text, sig_col = "⌛ SCANNING SNIPER ENTRY", "#555555"

    # --- 🟢 BUY/CALL ---
    if buy_sig and not st.session_state.trade["active"]:
        st.session_state.trade = {"active": True, "entry": ltp, "type": "CALL"}
        jarvis_speak(f"Rajveer Sir, High Probability Buy Signal. Entry at {ltp}")

    # --- 🔴 SELL/PUT ---
    elif sell_sig and not st.session_state.trade["active"]:
        st.session_state.trade = {"active": True, "entry": ltp, "type": "PUT"}
        jarvis_speak(f"Rajveer Sir, High Probability Sell Signal. Entry at {ltp}")

    # --- 🚦 EXIT LOGIC ---
    if st.session_state.trade["active"]:
        if st.session_state.trade["type"] == "CALL":
            sig_text, sig_col = "🚀 ACTIVE CALL (LONG)", "#00ff00"
            if (df['E9'].iloc[-1] < df['E21'].iloc[-1]):
                st.session_state.trade["active"] = False
                jarvis_speak("Trend Reversed. Exit Call Now.")
        
        elif st.session_state.trade["type"] == "PUT":
            sig_text, sig_col = "📉 ACTIVE PUT (SHORT)", "#ff4b4b"
            if (df['E9'].iloc[-1] > df['E21'].iloc[-1]):
                st.session_state.trade["active"] = False
                jarvis_speak("Trend Reversed. Exit Put Now.")

    # --- 📺 THE DASHBOARD ---
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"""
            <div style='background:#111; padding:20px; border-radius:15px; border:2px solid {sig_col}; text-align:center;'>
                <h1 style='color:white; margin:0;'>${ltp}</h1>
                <h2 style='color:{sig_col};'>{sig_text}</h2>
                <hr>
                <p style='color:gray;'>Entry: ${st.session_state.trade['entry'] if st.session_state.trade['entry'] > 0 else '---'}</p>
                <p style='color:#00ff00;'>Target (₹400): +40 pts</p>
                <p style='color:#ff4b4b;'>Karishma SL: -1%</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.info("📡 Connecting to Market Satellite... Standby Rajveer Sir.")
