import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. FAST REFRESH CONFIG ---
st.set_page_config(page_title="Jarvis R: Zero-Lag", layout="wide")
st_autorefresh(interval=1000, key="jarvis_r_zero_lag") # 1-Second Sync

# --- 🔊 2. VOICE ENGINE ---
def jarvis_r_speak(text, alert_type="normal"):
    beep = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if alert_type == "normal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js = f"""
    <script>
    window.speechSynthesis.cancel();
    new Audio('{beep}').play();
    var m = new SpeechSynthesisUtterance('{text}');
    m.lang = 'hi-IN'; m.rate = 1.1;
    window.speechSynthesis.speak(m);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🧠 3. LIGHTNING DATA ENGINE (CryptoCompare) ---
def get_fast_data():
    # यह API सीधे एक्सचेंज से डेटा उठाती है
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=100"
    try:
        response = requests.get(url).json()
        data = response['Data']['Data']
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except:
        return pd.DataFrame()

st.markdown("<h1 style='text-align:center; color:#f7931a;'>⚡ Jarvis R: Zero-Lag Sniper</h1>", unsafe_allow_html=True)

# State Management
if "r_entry" not in st.session_state: st.session_state.r_entry = 0.0
if "r_last_sig" not in st.session_state: st.session_state.r_last_sig = ""

# --- 🚀 4. EXECUTION ---
df = get_fast_data()

if not df.empty:
    ltp = float(df['close'].iloc[-1])
    # Calculations
    df['E9'] = df['close'].ewm(span=9).mean()
    df['E21'] = df['close'].ewm(span=21).mean()
    df['E200'] = df['close'].ewm(span=200).mean()

    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    # Entry Logic
    if buy_sig and st.session_state.r_last_sig != "BUY":
        st.session_state.r_last_sig = "BUY"
        st.session_state.r_entry = ltp
        jarvis_r_speak(f"Jarvis R Buy Signal at {ltp}")
    elif sell_sig and st.session_state.r_last_sig != "SELL":
        st.session_state.r_last_sig = "SELL"
        st.session_state.r_entry = ltp
        jarvis_r_speak(f"Jarvis R Sell Signal at {ltp}")

    # PNL & Alerts
    if st.session_state.r_entry > 0:
        pnl = ltp - st.session_state.r_entry if st.session_state.r_last_sig == "BUY" else st.session_state.r_entry - ltp
        
        # Trend Hunter Logic
        if pnl >= 300:
            jarvis_r_speak("Rajveer Sir, ruko nahi! Trend abhi bhi strong hai.")
        
        # Stop Loss & Reverse Trend
        reversal = (st.session_state.r_last_sig == "BUY" and ltp < df['E9'].iloc[-1]) or \
                   (st.session_state.r_last_sig == "SELL" and ltp > df['E9'].iloc[-1])
        if reversal and pnl > 50:
            jarvis_r_speak("Exit now! Trend ulat raha hai.", alert_type="emergency")
            st.session_state.r_entry = 0
            st.session_state.r_last_sig = "EXIT"

    # --- 📺 UI ---
    c1, c2, c3 = st.columns(3)
    c1.metric("BTC FAST PRICE", f"${ltp}")
    c2.metric("CURRENT POSITION", st.session_state.r_last_sig)
    c3.metric("LIVE PNL", f"{round(pnl, 2) if st.session_state.r_entry > 0 else 0}")

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
