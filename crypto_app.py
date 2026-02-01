import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="Jarvis R: Supreme Hunter", layout="wide")
st_autorefresh(interval=1000, key="jarvis_supreme_v23")

# --- 🔊 2. VOICE ENGINE ---
def jarvis_r_speak(text, alert_type="normal"):
    beep = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if alert_type == "normal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js = f"""
    <script>
    window.speechSynthesis.cancel();
    new Audio('{beep}').play();
    var m = new SpeechSynthesisUtterance('{text}');
    m.lang = 'hi-IN'; m.rate = 1.0;
    window.speechSynthesis.speak(m);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🧠 3. FAST DATA ENGINE ---
def get_fast_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=100"
    try:
        response = requests.get(url).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return pd.DataFrame()

st.markdown("<h1 style='text-align:center; color:#f7931a;'>🚀 JARVIS-R: SUPREME MOMENTUM HUNTER</h1>", unsafe_allow_html=True)

# State Management
if "entry_p" not in st.session_state: st.session_state.entry_p = 0.0
if "last_s" not in st.session_state: st.session_state.last_s = ""
if "hunter_mode" not in st.session_state: st.session_state.hunter_mode = False

# --- 🚀 4. EXECUTION & STRATEGY VOTING ---
df = get_fast_data()

if not df.empty:
    ltp = float(df['close'].iloc[-1])
    
    # Background Strategies Calculation
    df['E9'] = df['close'].ewm(span=9).mean()
    df['E21'] = df['close'].ewm(span=21).mean()
    df['E200'] = df['close'].ewm(span=200).mean()
    # RSI for Strength
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Voting System
    score = 0
    if df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1]: score += 1 # Javed Logic
    if df['RSI'].iloc[-1] > 50: score += 1 # Momentum Logic
    if ltp > df['high'].iloc[-2]: score += 1 # Breakout Logic

    # High Probability Signal (Score >= 2)
    if score >= 2 and st.session_state.last_s != "BUY":
        st.session_state.last_s = "BUY"
        st.session_state.entry_p = ltp
        jarvis_r_speak(f"Master Buy Entry at {ltp}. High probability momentum ahead.")

    elif score <= 0 and st.session_state.last_s != "SELL":
        st.session_state.last_s = "SELL"
        st.session_state.entry_p = ltp
        jarvis_r_speak(f"Master Sell Entry at {ltp}. Trend is crashing.")

    # --- 🛡️ MOMENTUM & TARGET TRACKING ---
    pnl = 0.0
    if st.session_state.entry_p > 0:
        pnl = round(ltp - st.session_state.entry_p if st.session_state.last_s == "BUY" else st.session_state.entry_p - ltp, 2)
        
        # Hunter Mode Voice (250, 300, 500 Pts)
        if pnl >= 250 and pnl < 500:
            if not st.session_state.hunter_mode:
                jarvis_r_speak("Rajveer Sir, 250 point paar! Trend bahut majboot hai, ruko nahi!")
                st.session_state.hunter_mode = True
        elif pnl >= 500:
            jarvis_r_speak("Jackpot! 500 points achieved. Ab profit book karne ka socho!", alert_type="emergency")

        # Exit if trend reverses against strategy
        if (st.session_state.last_s == "BUY" and ltp < df['E9'].iloc[-1]) or \
           (st.session_state.last_s == "SELL" and ltp > df['E9'].iloc[-1]):
            if pnl > 50: # Only exit if some profit was there or SL hit
                jarvis_r_speak("Exit! Market trend ke against ja raha hai.", alert_type="emergency")
                st.session_state.entry_p = 0.0
                st.session_state.last_s = "EXIT"

    # --- 📺 DASHBOARD ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("LTP", f"${ltp}")
    col2.metric("ENTRY PRICE", f"${st.session_state.entry_p if st.session_state.entry_p > 0 else '---'}")
    col3.metric("SIGNAL", st.session_state.last_s)
    col4.metric("LIVE PNL", f"{pnl} Pts", delta=pnl)

    # Big Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA (The Wall)', line=dict(color='orange', width=2)))
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

if st.button("🔄 Reset Jarvis R for Next Hunting"):
    st.session_state.entry_p = 0.0
    st.session_state.last_s = ""
    st.session_state.hunter_mode = False
    st.rerun()
