import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- 🎯 1. SNIPER CONFIGURATION ---
st.set_page_config(page_title="JARVIS-R: FINAL", layout="wide")
# 1-second no-blink refresh
st_autorefresh(interval=1000, key="jarvis_final_refresh")

# --- 🧠 2. SMART DATA ENGINE ---
def get_live_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔊 3. BACKGROUND VOICE & SIREN ENGINE ---
def jarvis_emergency_alert(text, type="signal"):
    # Siren sound + Voice
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if type=="signal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js_code = f"""
    <script>
    var audio = new Audio('{siren_url}');
    audio.play();
    var msg = new SpeechSynthesisUtterance('{text}');
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🏦 4. BRANDING & DASHBOARD ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #000, #ff4b4b); padding:10px; border-radius:15px; border:2px solid #fff;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: FINAL SNIPER</h1>
        <p style='color:white; margin:0; font-weight:bold;'>200-300 PT MOMENTUM | TIGHT SL | VOICE v7.0</p>
    </div>
    <p style='text-align:center; color:gray; font-size:12px;'>राजवीर सर: वॉइस एक्टिव करने के लिए स्क्रीन पर एक बार कहीं भी क्लिक करें।</p>
""", unsafe_allow_html=True)

# Session States
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "trade" not in st.session_state: st.session_state.trade = {"active": False, "entry": 0.0, "type": ""}

# --- 🚀 5. SNIPER LOGIC (45-POINTS + VOLATILITY) ---
coin = "BTC-USD"
df = get_live_data(coin)

if df is not None and len(df) > 50:
    ltp = round(float(df['Close'].iloc[-1]), 2)
    df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # Big Move Detection (ATR)
    df['TR'] = df['High'] - df['Low']
    atr_spike = df['TR'].iloc[-1] > (df['TR'].rolling(20).mean().iloc[-1] * 1.5)
    
    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1]) and atr_spike
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1]) and atr_spike

    # --- 🚦 EXECUTION ---
    if buy_sig and st.session_state.last_sig != "BUY":
        st.session_state.last_sig = "BUY"
        st.session_state.trade = {"active": True, "entry": ltp, "type": "CALL"}
        jarvis_emergency_alert(f"Rajveer Sir, Master Buy Entry Detected. Targeting 300 points.")

    elif sell_sig and st.session_state.last_sig != "SELL":
        st.session_state.last_sig = "SELL"
        st.session_state.trade = {"active": True, "entry": ltp, "type": "PUT"}
        jarvis_emergency_alert(f"Rajveer Sir, High Volume Sell Detected. Trend is crashing.")

    # --- 🛡️ TIGHT STOP LOSS (0.3% Karishma Guard) ---
    if st.session_state.trade["active"]:
        entry = st.session_state.trade["entry"]
        sl = entry * 0.997 if st.session_state.trade["type"] == "CALL" else entry * 1.003
        
        # Exit Condition
        if (st.session_state.trade["type"] == "CALL" and ltp <= sl) or \
           (st.session_state.trade["type"] == "PUT" and ltp >= sl):
            st.session_state.trade["active"] = False
            st.session_state.last_sig = ""
            jarvis_emergency_alert("Emergency Exit! Stop Loss Triggered to save capital.", type="exit")

    # --- 📺 DISPLAY COMMAND CENTER ---
    c1, c2, c3 = st.columns(3)
    c1.metric("LIVE PRICE", f"${ltp}")
    c2.metric("CURRENT SIGNAL", st.session_state.last_sig if st.session_state.last_sig else "SCANNING")
    c3.metric("TIGHT SL", "0.3% ACTIVE", delta="Capital Protected")

    col_chart, col_stats = st.columns([2, 1])
    with col_chart:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_stats:
        status_col = "#00ff00" if st.session_state.last_sig == "BUY" else "#ff4b4b" if st.session_state.last_sig == "SELL" else "#555555"
        st.markdown(f"""
            <div style='background:#111; padding:20px; border-radius:15px; border:2px solid {status_col}; text-align:center;'>
                <h3 style='color:gray;'>Target: +200-300 Pts</h3>
                <h2 style='color:{status_col};'>{st.session_state.last_sig if st.session_state.last_sig else "WAITING..."}</h2>
                <p style='color:white;'>Entry: ${st.session_state.trade['entry'] if st.session_state.trade['entry'] > 0 else '---'}</p>
                <p style='color:orange;'>Siren Status: STANDBY 🔊</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("📡 Connecting to Jarvis-R Satellite... Please click once on the screen Rajveer Sir.")
