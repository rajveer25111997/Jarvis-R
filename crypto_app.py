import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS v54: MOMENTUM SIGNAL", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v54_fix")

# Custom CSS for Visibility
st.markdown("""
    <style>
    .main { background-color: #06090F; }
    .signal-box { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 15px; }
    .price-text { font-size: 30px; color: #00FFCC; font-family: 'Courier New'; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔊 2. VOICE & WAKE LOCK FIX (Direct JS) ---
def jarvis_voice_engine(text, alert_type="normal"):
    siren = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    js_code = f"""
    <script>
    // Wake Lock: Device ko sone se rokne ke liye
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(e => {{}}); }}
    
    // Voice & Sound
    window.speechSynthesis.cancel();
    var audio = new Audio('{siren}');
    audio.play();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        msg.rate = 1.1;
        window.speechSynthesis.speak(msg);
    }}, 800);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: MOMENTUM HUNTER v54.0</h1>", unsafe_allow_html=True)

if st.button("📢 START JARVIS SYSTEM (Voice & Signal Fix)"):
    jarvis_voice_engine("System Online. Voice and Momentum Signal Active.")

# --- 🧠 3. STATE ---
for k in ["st_last", "st_ep", "st_tg", "r_last", "r_ep", "r_tg"]:
    if k not in st.session_state: st.session_state[k] = "" if "last" in k else 0.0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE MOMENTUM SIGNAL ---
with col_st:
    st.markdown("<h2 style='color:#007BFF; text-align:center;'>📈 NSE SIGNAL</h2>", unsafe_allow_html=True)
    asset_st = st.sidebar.selectbox("Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    tk = yf.Ticker(asset_st)
    df_st = tk.history(period="2d", interval="1m")
    
    if not df_st.empty:
        ltp = float(df_st['Close'].iloc[-1])
        day_open = float(df_st['Open'].iloc[0])
        mom_pts = round(ltp - day_open, 2)
        
        # EMA for Javed Strategy
        e9 = df_st['Close'].ewm(span=9).mean().iloc[-1]
        e21 = df_st['Close'].ewm(span=21).mean().iloc[-1]

        # MOMENTUM BASED SIGNAL
        # Call tabhi jab 9>21 ho aur momentum positive ho
        if e9 > e21 and mom_pts > 0 and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
            st.session_state.st_tg = ltp + 60
            jarvis_voice_engine(f"Rajveer Sir, Strong Momentum! Stock Call Buy. Target {st.session_state.st_tg:.2f}")
        elif e9 < e21 and mom_pts < 0 and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
            st.session_state.st_tg = ltp - 60
            jarvis_voice_engine(f"Rajveer Sir, Sharp Fall! Stock Put Buy. Target {st.session_state.st_tg:.2f}")

        # UI Signal Box
        bg_color = "#1E5631" if "CALL" in st.session_state.st_last else "#800000" if "PUT" in st.session_state.st_last else "#1B2631"
        st.markdown(f"<div class='signal-box' style='background-color:{bg_color};'>SIGNAL: {st.session_state.st_last} | MOM: {mom_pts} Pts</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.markdown(f"**LIVE:** <span class='price-text'>{ltp:.2f}</span>", unsafe_allow_html=True)
        c2.markdown(f"**TARGET:** <span class='price-text'>{st.session_state.st_tg:.2f}</span>", unsafe_allow_html=True)

        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO MOMENTUM SIGNAL ---
with col_cr:
    st.markdown("<h2 style='color:#F7931A; text-align:center;'>₿ CRYPTO SIGNAL</h2>", unsafe_allow_html=True)
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=100").json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            ltp_r = float(df_cr['close'].iloc[-1])
            cr_open = float(df_cr['open'].iloc[0])
            mom_r = round(ltp_r - cr_open, 2)

            if ltp_r > df_cr['close'].ewm(span=9).mean().iloc[-1] and mom_r > 50 and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_r
                st.session_state.r_tg = ltp_r + 250
                jarvis_voice_engine(f"Crypto Hunter Alert! Bitcoin Call Buy. Target {st.session_state.r_tg}")
            elif ltp_r < df_cr['close'].ewm(span=9).mean().iloc[-1] and mom_r < -50 and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r
                st.session_state.r_tg = ltp_r - 250
                jarvis_voice_engine(f"Crypto Hunter Alert! Bitcoin Put Buy. Target {st.session_state.r_tg}")

            bg_cr = "#1E5631" if "CALL" in st.session_state.r_last else "#800000" if "PUT" in st.session_state.r_last else "#1B2631"
            st.markdown(f"<div class='signal-box' style='background-color:{bg_cr};'>CRYPTO: {st.session_state.r_last} | MOM: ${mom_r}</div>", unsafe_allow_html=True)
            
            d1, d2 = st.columns(2)
            d1.markdown(f"**LIVE:** <span class='price-text'>${ltp_r:.2f}</span>", unsafe_allow_html=True)
            d2.markdown(f"**TARGET:** <span class='price-text'>${st.session_state.r_tg:.2f}</span>", unsafe_allow_html=True)

            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("Connecting...")
