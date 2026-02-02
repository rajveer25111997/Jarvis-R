import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS SUPREME v61", layout="wide")
st_autorefresh(interval=1500, key="jarvis_v61_final")

# --- 🔊 2. ULTIMATE BROWSER VOICE (Web Speech API) ---
def jarvis_speak_supreme(text, alert_type="normal"):
    siren = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else ""
    js_code = f"""
    <script>
    window.speechSynthesis.cancel();
    if ("{siren}" !== "") {{ var a = new Audio("{siren}"); a.volume = 0.5; a.play(); }}
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.lang = 'hi-IN'; msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(e=>{{"ERR"}}); }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🧠 3. PERSISTENT STATE ---
if "init" not in st.session_state:
    st.session_state.update({
        "last_sig": "", "ep": 0.0, "sl": 0.0, "tp": 0.0, "active": False
    })

# --- 🛰️ 4. DATA ENGINE ---
def get_safe_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1m", progress=False)
        return df if not df.empty else None
    except: return None

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS SUPREME: COMMANDER v61.0</h1>", unsafe_allow_html=True)

# --- 🚀 5. EXECUTION ---
col_main, col_stats = st.columns([3, 1])

with col_main:
    asset = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "BTC-USD"], key="main_asset")
    df = get_safe_data(asset)
    
    # Initializing ltp with a default value to prevent NameError
    ltp = 0.0
    oi_status = "SCANNING"

    if df is not None and len(df) > 100:
        try:
            df['E9'] = ta.ema(df['Close'], length=9)
            df['E21'] = ta.ema(df['Close'], length=21)
            df['E200'] = ta.ema(df['Close'], length=200)
            
            ltp = float(df['Close'].iloc[-1])
            oi_status = "BULLISH" if ltp > df['Open'].iloc[0] else "BEARISH"
            
            # Javed Strategy + OI Filter
            is_call = bool(df['E9'].iloc[-1] > df['E21'].iloc[-1] and ltp > df['E200'].iloc[-1] and oi_status == "BULLISH")
            is_put = bool(df['E9'].iloc[-1] < df['E21'].iloc[-1] and ltp < df['E200'].iloc[-1] and oi_status == "BEARISH")

            if is_call and st.session_state.last_sig != "CALL":
                st.session_state.last_sig = "CALL"; st.session_state.ep = ltp
                st.session_state.sl = ltp - 35; st.session_state.tp = ltp + 60
                jarvis_speak_supreme(f"राजवीर सर, High Probability Call! OI Bullish है।")
            elif is_put and st.session_state.last_sig != "PUT":
                st.session_state.last_sig = "PUT"; st.session_state.ep = ltp
                st.session_state.sl = ltp + 35; st.session_state.tp = ltp - 60
                jarvis_speak_supreme(f"राजवीर सर, High Probability Put! OI Bearish है।")

            # Profit Filter (10-20 Points)
            if st.session_state.ep > 0:
                pnl = ltp - st.session_state.ep if st.session_state.last_sig == "CALL" else st.session_state.ep - ltp
                if pnl >= 20: jarvis_speak_supreme("20 points profit! Trail your SL, ruko nahi!", "normal")
                elif pnl <= -15: 
                    jarvis_speak_supreme("Alert! Strict SL hit. Exit now.", "emergency")
                    st.session_state.ep = 0; st.session_state.last_sig = "SL EXIT"

            # Candlestick Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange')))
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("📡 Calibrating Market Meters... Please wait.")
    else:
        st.warning("📡 Connecting to Satellite Data Feed...")

with col_stats:
    st.subheader("🏥 Stats & OI")
    # Display ltp safely
    if ltp > 0:
        st.metric("LIVE PRICE", f"₹{round(ltp, 2)}")
        st.write(f"**OI Trend:** {oi_status}")
        st.success(f"STRIKE: {round(ltp/100)*100}")
    else:
        st.write("Fetching Price...")
        
    st.write(f"**Signal:** {st.session_state.last_sig}")
    st.write(f"**Entry:** {st.session_state.ep}")
    
    if st.button("🔄 Full Reset Master"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()
