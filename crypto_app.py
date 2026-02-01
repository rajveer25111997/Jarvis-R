import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="JARVIS-R: PROTECTOR", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v18_final")

# --- 🔊 2. VOICE ENGINE (No-Overlap Fix) ---
def jarvis_speak(text, type="signal"):
    siren = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if type=="signal" else "https://www.soundjay.com/buttons/sounds/beep-04.mp3"
    js_code = f"""
    <script>
    window.speechSynthesis.cancel(); // पुराने अलर्ट को तुरंत बंद करने के लिए
    var audio = new Audio('{siren}');
    audio.play();
    var msg = new SpeechSynthesisUtterance('{text}');
    msg.lang = 'hi-IN';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 📊 3. DATA ENGINE ---
def get_live_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 🏦 4. BRANDING ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #1e3c72, #2a5298); padding:10px; border-radius:15px; border:2px solid gold;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: PROTECTOR v18.0</h1>
        <p style='color:gold; margin:0;'>TARGET + SL VOICE ALERT | NSE & CRYPTO</p>
    </div>
""", unsafe_allow_html=True)

if st.button("📢 ACTIVATE JARVIS", use_container_width=True):
    jarvis_speak("System Active. Rajveer Sir, ab target aur stop loss dono par meri nazar hai.")

# State Management
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry_price" not in st.session_state: st.session_state.entry_price = 0.0
if "alert_done" not in st.session_state: st.session_state.alert_done = False

# --- 🚀 5. LOGIC ENGINE ---
asset = st.sidebar.selectbox("Market Asset:", ["^NSEI", "^NSEBANK", "BTC-USD", "RELIANCE.NS"])
df = get_live_data(asset)

if not df.empty and len(df) > 20:
    ltp = round(df['Close'].iloc[-1], 2)
    df['E9'] = df['Close'].ewm(span=9).mean()
    df['E21'] = df['Close'].ewm(span=21).mean()
    df['E200'] = df['Close'].ewm(span=200).mean()

    # Priority Signal Logic (Donon ek saath nahi bajenge)
    buy_cond = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_cond = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    # 🚦 SIGNAL TRIGGER
    if buy_cond and st.session_state.last_sig != "BUY":
        st.session_state.last_sig = "BUY"
        st.session_state.entry_price = ltp
        st.session_state.alert_done = False
        jarvis_speak(f"Master Buy Signal in {asset} at {ltp}.")

    elif sell_cond and st.session_state.last_sig != "SELL":
        st.session_state.last_sig = "SELL"
        st.session_state.entry_price = ltp
        st.session_state.alert_done = False
        jarvis_speak(f"Master Sell Signal in {asset} at {ltp}.")

    # 🛡️ TARGET & SL MONITOR (20 Point Target | 10 Point SL)
    if st.session_state.entry_price > 0 and not st.session_state.alert_done:
        pnl = ltp - st.session_state.entry_price if st.session_state.last_sig == "BUY" else st.session_state.entry_price - ltp
        
        # Target Alert (20 Points)
        if pnl >= 20:
            jarvis_speak("Rajveer Sir, Target Achieved! Paisa mil gaya hai, ab bahar niklo.", type="exit")
            st.session_state.alert_done = True
            st.balloons()
            
        # Karishma Stop Loss (10 Points)
        elif pnl <= -10:
            jarvis_speak("Emergency! Stop Loss hit ho gaya hai. Capital bachao aur exit karo.", type="exit")
            st.session_state.alert_done = True
            st.session_state.entry_price = 0

    # --- 📺 DISPLAY ---
    c1, c2, c3 = st.columns(3)
    c1.metric("LIVE PRICE", f"₹{ltp}")
    c2.metric("SIGNAL", st.session_state.last_sig)
    cur_pnl = round(ltp - st.session_state.entry_price if st.session_state.last_sig == "BUY" else st.session_state.entry_price - ltp, 2) if st.session_state.entry_price > 0 else 0
    c3.metric("CURRENT PNL", f"{cur_pnl} Pts")

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("🔄 Reset Trade (Agla Trade Leney Ke Liye)"):
        st.session_state.last_sig = ""
        st.session_state.entry_price = 0.0
        st.session_state.alert_done = False
        st.rerun()
