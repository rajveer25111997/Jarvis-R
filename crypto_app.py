import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- 🎯 1. TRADING TERMINAL CONFIG ---
st.set_page_config(page_title="JARVIS DUAL: TRADING MODE", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v50_final") # 1-Second Heartbeat

# Custom CSS for Professional Trading Look
st.markdown("""
    <style>
    .main { background-color: #06090F; }
    div[data-testid="stMetricValue"] { font-size: 45px !important; color: #00FFCC !important; font-weight: bold; }
    .stAlert { background-color: #1B2631; border: 1px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔊 2. EMERGENCY SIREN & HUNTER VOICE ---
def jarvis_emergency_system(text, alert_type="normal"):
    siren = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    js = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(e => {{}}); }}
    window.speechSynthesis.cancel();
    new Audio('{siren}').play();
    setTimeout(function() {{
        var m = new SpeechSynthesisUtterance('{text}');
        m.lang = 'hi-IN'; window.speechSynthesis.speak(m);
    }}, 1000);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🧠 3. PERSISTENT TRADING STATE ---
keys = ["st_last", "st_ep", "st_tg", "st_sl", "r_last", "r_ep", "r_tg", "r_sl"]
for k in keys:
    if k not in st.session_state: st.session_state[k] = "" if "last" in k else 0.0

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: TRADING TERMINAL v50.0</h1>", unsafe_allow_html=True)

if st.button("📢 START JARVIS HUNTER MODE (Activate Voice)"):
    jarvis_emergency_system("Trading Hunter Mode Active Rajveer Sir. Scanning for momentum.")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE INTRADAY (Stock/Index) ---
with col_st:
    st.markdown("<h2 style='color:#007BFF;'>📈 NSE INTRADAY</h2>", unsafe_allow_html=True)
    asset_st = st.sidebar.selectbox("Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    # Using Ticker for more precise live price
    tk = yf.Ticker(asset_st)
    df_st = tk.history(period="2d", interval="1m")
    
    if not df_st.empty and len(df_st) > 20:
        ltp_st = float(df_st['Close'].iloc[-1])
        df_st['E9'] = df_st['Close'].ewm(span=9).mean()
        df_st['E21'] = df_st['Close'].ewm(span=21).mean()
        df_st['E200'] = df_st['Close'].ewm(span=200).mean()
        
        e9, e21, e200 = df_st['E9'].iloc[-1], df_st['E21'].iloc[-1], df_st['E200'].iloc[-1]
        strike = round(ltp_st / 50 if "NSEI" in asset_st else ltp_st / 100) * (50 if "NSEI" in asset_st else 100)

        # 🚦 TRADING SIGNALS
        if e9 > e21 and ltp_st > e200 and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp_st
            st.session_state.st_tg = ltp_st + (ltp_st * 0.004); st.session_state.st_sl = ltp_st - (ltp_st * 0.002)
            jarvis_emergency_system(f"NSE Call Entry. Strike {strike} CE.")
        elif e9 < e21 and ltp_st < e200 and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp_st
            st.session_state.st_tg = ltp_st - (ltp_st * 0.004); st.session_state.st_sl = ltp_st + (ltp_st * 0.002)
            jarvis_emergency_system(f"NSE Put Entry. Strike {strike} PE.")

        # Display Metrics
        st.markdown(f"<h3 style='color:yellow; text-align:center;'>SIGNAL: {st.session_state.st_last} | ATM: {strike}</h3>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("LIVE PRICE", f"{ltp_st:.2f}")
        m2.metric("ENTRY", f"{st.session_state.st_ep:.2f}")
        m3.metric("TARGET", f"{st.session_state.st_tg:.2f}")

        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.add_trace(go.Scatter(x=df_st.index, y=df_st['E200'], name='200 EMA', line=dict(color='orange')))
        fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO SCALPING (Jarvis R) ---
with col_cr:
    st.markdown("<h2 style='color:#F7931A;'>₿ CRYPTO SCALPER</h2>", unsafe_allow_html=True)
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300", timeout=2).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = df_cr['close'].ewm(span=9).mean()
            df_cr['E21'] = df_cr['close'].ewm(span=21).mean()
            df_cr['E200'] = df_cr['close'].ewm(span=200).mean()
            ltp_r = float(df_cr['close'].iloc[-1])
            
            if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_r > df_cr['E200'].iloc[-1] and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_r
                st.session_state.r_tg = ltp_r + 300; st.session_state.r_sl = ltp_r - 150
                jarvis_emergency_system("Crypto Call Buy.")
            elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_r < df_cr['E200'].iloc[-1] and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r
                st.session_state.r_tg = ltp_r - 300; st.session_state.r_sl = ltp_r + 150
                jarvis_emergency_system("Crypto Put Buy.")

            st.markdown(f"<h3 style='color:yellow; text-align:center;'>SIGNAL: {st.session_state.r_last}</h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("LIVE PRICE", f"${ltp_r:.2f}")
            c2.metric("ENTRY", f"${st.session_state.r_ep:.2f}")
            c3.metric("TARGET", f"${st.session_state.r_tg:.2f}")

            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting Crypto Feed...")

if st.button("🔄 CLEAR ALL TRADES"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
