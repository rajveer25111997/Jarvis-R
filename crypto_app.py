import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="Jarvis R: Crypto Hunter", layout="wide")
st_autorefresh(interval=1000, key="jarvis_r_final_fix")

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

st.markdown("<h1 style='text-align:center; color:#f7931a;'>₿ Jarvis R: Crypto Hunter v21.0</h1>", unsafe_allow_html=True)

# State Management
if "r_entry" not in st.session_state: st.session_state.r_entry = 0.0
if "r_last_sig" not in st.session_state: st.session_state.r_last_sig = ""
if "r_notified" not in st.session_state: st.session_state.r_notified = False

# --- 🚀 3. DATA & SIGNAL ENGINE ---
# Error Fix: Ensuring data is valid before processing
try:
    df = yf.download("BTC-USD", period="1d", interval="1m", progress=False, auto_adjust=True)
    if not df.empty and len(df) > 21:
        # Columns flattening for consistency
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        ltp = float(df['Close'].iloc[-1])
        df['E9'] = df['Close'].ewm(span=9).mean()
        df['E21'] = df['Close'].ewm(span=21).mean()
        df['E200'] = df['Close'].ewm(span=200).mean()

        # Signal Logic
        is_buy = bool((df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1]))
        is_sell = bool((df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1]))

        # --- 🚦 ENTRY ALERTS ---
        if is_buy and st.session_state.r_last_sig != "BUY":
            st.session_state.r_last_sig = "BUY"
            st.session_state.r_entry = ltp
            st.session_state.r_notified = False
            jarvis_r_speak(f"Jarvis R: Master Buy Signal at {round(ltp, 2)}")

        elif is_sell and st.session_state.r_last_sig != "SELL":
            st.session_state.r_last_sig = "SELL"
            st.session_state.r_entry = ltp
            st.session_state.r_notified = False
            jarvis_r_speak(f"Jarvis R: Master Sell Signal at {round(ltp, 2)}")

        # --- 🛡️ TARGET, SL & TREND LOGIC ---
        if st.session_state.r_entry > 0:
            diff = ltp - st.session_state.r_entry if st.session_state.r_last_sig == "BUY" else st.session_state.r_entry - ltp
            
            # 1. Profit Trailing (Ruko Nahi Mode)
            if diff >= 300 and not st.session_state.r_notified:
                jarvis_r_speak("Rajveer Sir, bada munafa hai! Trend strong hai, abhi ruko nahi!")
                st.session_state.r_notified = True
            
            # 2. Reversal Alert (Exit Mode)
            reversal = (st.session_state.r_last_sig == "BUY" and ltp < df['E9'].iloc[-1]) or \
                       (st.session_state.r_last_sig == "SELL" and ltp > df['E9'].iloc[-1])
            
            if reversal and diff > 50:
                jarvis_r_speak("Chetavani! Trend ulat raha hai. Exit! Turant bahar niklo!", alert_type="emergency")
                st.session_state.r_entry = 0
                st.session_state.r_last_sig = "EXIT"

            # 3. Karishma SL (0.3% Hard Stop)
            if diff <= -(st.session_state.r_entry * 0.003):
                jarvis_r_speak("Emergency! Karishma Stop Loss hit. Capital bachao, exit karo!", alert_type="emergency")
                st.session_state.r_entry = 0
                st.session_state.r_last_sig = "SL_HIT"

        # --- 📺 DISPLAY ---
        c1, c2, c3 = st.columns(3)
        c1.metric("LIVE BTC", f"${round(ltp, 2)}")
        c2.metric("SIGNAL", st.session_state.r_last_sig)
        pnl = round(ltp - st.session_state.r_entry if st.session_state.r_last_sig == "BUY" else st.session_state.r_entry - ltp, 2) if st.session_state.r_entry > 0 else 0
        c3.metric("LIVE PNL", f"{pnl} Pts", delta=pnl)

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E9'], name='Trend (9)', line=dict(color='cyan')))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("📡 Connecting to Satellite Data...")

except Exception as e:
    st.error(f"Waiting for stable data... (System auto-recovering)")

if st.button("🔄 Manual Reset Jarvis R"):
    st.session_state.r_entry = 0.0
    st.session_state.r_last_sig = ""
    st.rerun()
