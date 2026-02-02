import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME SETTINGS ---
st.set_page_config(page_title="JARVIS v49: VISIBILITY FIX", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v49_master")

# CSS for Dark Theme and Big Text (सफ़ेद बैकग्राउंड को खत्म करने के लिए)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 40px; color: #00FF00; font-weight: bold; }
    label[data-testid="stMetricLabel"] { font-size: 20px; color: #FFD700; }
    </style>
    """, unsafe_allow_html=True)

def jarvis_emergency_system(text):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(err => {{}}); }}
    new Audio('{siren_url}').play();
    window.speechSynthesis.cancel();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN'; window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🧠 2. STATE RECOVERY ---
# इन कीज़ को सेव रखना ज़रूरी है ताकि टारगेट 0 न हो
keys = ["st_last", "st_ep", "st_sl", "st_tg", "r_last", "r_ep", "r_sl", "r_tg"]
for k in keys:
    if k not in st.session_state: st.session_state[k] = "" if "last" in k else 0.0

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS DUAL: VISUAL STATION v49.0</h1>", unsafe_allow_html=True)

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK MARKET ---
with col_st:
    st.markdown("<h2 style='color:#007BFF;'>📈 NSE STATION</h2>", unsafe_allow_html=True)
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = yf.download(asset_st, period="5d", interval="1m", progress=False)
    
    if not df_st.empty and len(df_st) > 20:
        df_st['E9'] = df_st['Close'].ewm(span=9).mean()
        df_st['E21'] = df_st['Close'].ewm(span=21).mean()
        df_st['E200'] = df_st['Close'].ewm(span=200).mean()
        
        ltp = float(df_st['Close'].iloc[-1])
        e9, e21, e200 = df_st['E9'].iloc[-1], df_st['E21'].iloc[-1], df_st['E200'].iloc[-1]
        strike = round(ltp / 50 if "NSEI" in asset_st else ltp / 100) * (50 if "NSEI" in asset_st else 100)

        # Signal logic & persistent Target/SL
        if e9 > e21 and ltp > e200 and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
            st.session_state.st_sl = round(ltp - (ltp * 0.002), 1); st.session_state.st_tg = round(ltp + (ltp * 0.005), 1)
            jarvis_emergency_system(f"NSE Alert! Call Signal. Entry {ltp}.")
        elif e9 < e21 and ltp < e200 and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
            st.session_state.st_sl = round(ltp + (ltp * 0.002), 1); st.session_state.st_tg = round(ltp - (ltp * 0.005), 1)
            jarvis_emergency_system(f"NSE Alert! Put Signal. Entry {ltp}.")

        # Visibility Boxes
        st.markdown(f"<div style='background-color:#1B2631; padding:10px; border-radius:5px; text-align:center;'><b>SIGNAL: {st.session_state.st_last} | STRIKE: {strike}</b></div>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("LIVE ₹", f"{round(ltp,1)}")
        m2.metric("TARGET", f"{st.session_state.st_tg}")
        m3.metric("ENTRY", f"{st.session_state.st_ep}")

        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO MASTER ---
with col_cr:
    st.markdown("<h2 style='color:#F7931A;'>₿ CRYPTO MASTER</h2>", unsafe_allow_html=True)
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
                jarvis_emergency_system("Crypto Alert! Bitcoin Call Buy.")
            elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_r < df_cr['E200'].iloc[-1] and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r
                st.session_state.r_tg = ltp_r - 300; st.session_state.r_sl = ltp_r + 150
                jarvis_emergency_system("Crypto Alert! Bitcoin Put Buy.")

            st.markdown(f"<div style='background-color:#1B2631; padding:10px; border-radius:5px; text-align:center;'><b>SIGNAL: {st.session_state.r_last}</b></div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("LIVE $", f"{round(ltp_r,1)}")
            c2.metric("TARGET", f"{st.session_state.r_tg}")
            c3.metric("ENTRY", f"{st.session_state.r_ep}")

            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting Crypto Feed...")

if st.button("🔄 Reset Master System"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
