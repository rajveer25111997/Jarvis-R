import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 Jarvis R Configuration ---
st.set_page_config(page_title="Jarvis R: Crypto Hunter", layout="wide")
st_autorefresh(interval=1000, key="jarvis_r_v20")

# --- 🔊 Ultra-Fast Voice Engine ---
def jarvis_r_speak(text, alert_type="normal"):
    # alert_type "emergency" के लिए तेज़ सायरन
    beep = "https://www.soundjay.com/buttons/sounds/beep-04.mp3" if alert_type == "normal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
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

st.markdown("<h1 style='text-align:center; color:#f7931a;'>₿ Jarvis R: Crypto Hunter</h1>", unsafe_allow_html=True)

# State Management for Jarvis R
if "r_entry" not in st.session_state: st.session_state.r_entry = 0.0
if "r_last_sig" not in st.session_state: st.session_state.r_last_sig = ""
if "r_trend" not in st.session_state: st.session_state.r_trend = "Neutral"

# --- 🧠 Data Engine ---
df = yf.download("BTC-USD", period="1d", interval="1m", progress=False, auto_adjust=True)

if not df.empty:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    df['E200'] = df['Close'].ewm(span=200).mean()

    # Strategy: Javed (9/21) + 200 EMA
    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    # --- 🚦 Jarvis R Entry Logic ---
    if buy_sig and st.session_state.r_last_sig != "BUY":
        st.session_state.r_last_sig = "BUY"
        st.session_state.r_entry = ltp
        jarvis_r_speak(f"Jarvis R Signal: Master Buy Bitcoin at {ltp}")

    elif sell_sig and st.session_state.r_last_sig != "SELL":
        st.session_state.r_last_sig = "SELL"
        st.session_state.r_entry = ltp
        jarvis_r_speak(f"Jarvis R Signal: Master Sell Bitcoin at {ltp}")

    # --- 🛡️ Hunter & Protector Logic (Target/SL) ---
    if st.session_state.r_entry > 0:
        # Profit/Loss Calculation
        diff = ltp - st.session_state.r_entry if st.session_state.r_last_sig == "BUY" else st.session_state.r_entry - ltp
        
        # 🟢 Condition 1: Profit is Growing (Ruko Nahi Mode)
        if diff >= 300: # 300 points threshold
            if ltp > df['E9'].iloc[-1] if st.session_state.r_last_sig == "BUY" else ltp < df['E9'].iloc[-1]:
                if st.session_state.r_trend != "Strong":
                    jarvis_r_speak("Rajveer Sir, bada munafa ho raha hai. Trend strong hai, ruko nahi!")
                    st.session_state.r_trend = "Strong"
        
        # 🔴 Condition 2: Trend Reversal (Exit Mode)
        # अगर प्राइस 9 EMA के वापस अंदर आ जाए (Trend पलटने का संकेत)
        reversal = (st.session_state.r_last_sig == "BUY" and ltp < df['E9'].iloc[-1]) or \
                   (st.session_state.r_last_sig == "SELL" and ltp > df['E9'].iloc[-1])
        
        if reversal and diff > 50:
            jarvis_r_speak("Warning! Market trend ke against ja raha hai. Exit! Exit!", alert_type="emergency")
            st.session_state.r_entry = 0
            st.session_state.r_last_sig = "EXITED"
            st.session_state.r_trend = "Neutral"

        # ❌ Condition 3: Karishma SL (Hard Stop)
        sl_limit = st.session_state.r_entry * 0.003
        if diff < -sl_limit:
            jarvis_r_speak("Emergency! Karishma Stop Loss hit. Exit immediately.", alert_type="emergency")
            st.session_state.r_entry = 0
            st.session_state.r_last_sig = "SL_HIT"

    # --- 📺 Command Center ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Live BTC", f"${ltp}")
    c2.metric("Signal Status", st.session_state.r_last_sig)
    pnl_show = round(ltp - st.session_state.r_entry if st.session_state.r_last_sig == "BUY" else st.session_state.r_entry - ltp, 2) if st.session_state.r_entry > 0 else 0
    c3.metric("Live PNL", f"{pnl_show} Pts")

    # Chart Display
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='Trend Line (9)', line=dict(color='cyan', width=1)))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

if st.button("🔄 Reset Jarvis R"):
    st.session_state.r_entry = 0.0
    st.session_state.r_last_sig = ""
    st.session_state.r_trend = "Neutral"
    st.rerun()
