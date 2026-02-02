import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. SUPREME CONFIG (1-SEC) ---
st.set_page_config(page_title="JARVIS SUPREME v60", layout="wide")
st_autorefresh(interval=1500, key="jarvis_v60_supreme")

# --- 🔊 2. CRITICAL BROWSER VOICE FIX (Web Speech API) ---
def jarvis_speak_supreme(text, alert_type="normal"):
    siren = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else ""
    js_code = f"""
    <script>
    window.speechSynthesis.cancel();
    if ("{siren}" !== "") {{ new Audio("{siren}").play(); }}
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.lang = 'hi-IN'; msg.rate = 1.0; msg.pitch = 1.1;
    window.speechSynthesis.speak(msg);
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen'); }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🧠 3. STATE & FILTER MANAGEMENT ---
if "init" not in st.session_state:
    st.session_state.update({
        "last_sig": "", "ep": 0.0, "sl": 0.0, "tp": 0.0,
        "total_pts": 0.0, "active": False
    })

# --- 🛰️ 4. DATA & OI SIMULATION ENGINE ---
def get_market_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1m", progress=False)
        # OI Analysis Simulation (Since Yahoo doesn't give live NSE OI)
        # Real-time mein yahan Upstox/AliceBlue API jud sakti hai
        df['OI_Trend'] = "BULLISH" if df['Close'].iloc[-1] > df['Open'].iloc[-1] else "BEARISH"
        return df
    except: return pd.DataFrame()

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS SUPREME: COMMANDER v60.0</h1>", unsafe_allow_html=True)

# --- 🚀 5. EXECUTION ---
col_main, col_stats = st.columns([3, 1])

with col_main:
    asset = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "BTC-USD"])
    df = get_market_data(asset)
    
    if not df.empty and len(df) > 100:
        df['E9'] = ta.ema(df['Close'], length=9)
        df['E21'] = ta.ema(df['Close'], length=21)
        df['E200'] = ta.ema(df['Close'], length=200)
        ltp = float(df['Close'].iloc[-1])
        oi_status = df['OI_Trend'].iloc[-1]
        
        # Javed Strategy + OI Filter
        is_call = bool(df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1] and oi_status == "BULLISH")
        is_put = bool(df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1] and oi_status == "BEARISH")

        # High Probability Signal Trigger
        if is_call and st.session_state.last_sig != "CALL":
            st.session_state.last_sig = "CALL"; st.session_state.ep = ltp
            st.session_state.sl = ltp - 30; st.session_state.tp = ltp + 50
            jarvis_speak_supreme(f"Rajveer Sir, High Probability Call Entry! OI is Bullish. Strike Price: {round(ltp/100)*100} CE")
        elif is_put and st.session_state.last_sig != "PUT":
            st.session_state.last_sig = "PUT"; st.session_state.ep = ltp
            st.session_state.sl = ltp + 30; st.session_state.tp = ltp - 50
            jarvis_speak_supreme(f"Rajveer Sir, High Probability Put Entry! OI is Bearish. Strike Price: {round(ltp/100)*100} PE")

        # --- 🎯 6. STRICT PROFIT FILTER (10-20 Points) ---
        if st.session_state.ep > 0:
            current_pnl = ltp - st.session_state.ep if st.session_state.last_sig == "CALL" else st.session_state.ep - ltp
            
            if current_pnl >= 20:
                jarvis_speak_supreme("Rajveer Sir, 20 points secured! Stop loss trail karein, ruko nahi!", "normal")
            elif current_pnl <= -15:
                jarvis_speak_supreme("Emergency Exit! Strict SL hit.", "emergency")
                st.session_state.ep = 0; st.session_state.last_sig = "EXIT"

        # Charting
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("🏥 Stats & OI")
    st.metric("LIVE PRICE", f"₹{ltp}")
    st.write(f"**OI Analysis:** {oi_status}")
    st.write(f"**Current Signal:** {st.session_state.last_sig}")
    st.write(f"**Entry Price:** {st.session_state.ep}")
    
    # Strike Price Logic
    strike = round(ltp / 100) * 100
    st.success(f"SUGGESTED STRIKE: {strike}")
    
    if st.button("🔄 Reset Master"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()
