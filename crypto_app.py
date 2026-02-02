import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG (1-SEC) ---
st.set_page_config(page_title="JARVIS DUAL: MASTER", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v46_final")

# --- 🔊 2. EMERGENCY SIREN & VOICE ---
def jarvis_emergency_system(text, alert_type="normal"):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(err => {{}}); }}
    window.speechSynthesis.cancel();
    var siren = new Audio('{siren_url}'); siren.play();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN'; window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS DUAL: MASTER COMMAND CENTER</h1>", unsafe_allow_html=True)

# State Management
for key in ["st_last", "st_ep", "r_last", "r_ep"]:
    if key not in st.session_state: st.session_state[key] = "" if "last" in key else 0.0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE) ---
with col_st:
    st.subheader("📈 STOCK: JAVED & KARISHMA")
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = yf.download(asset_st, period="5d", interval="1m", progress=False)
    
    if not df_st.empty and len(df_st) > 200:
        try:
            # EMA Calculations (No External Library needed)
            df_st['E9'] = df_st['Close'].ewm(span=9).mean()
            df_st['E21'] = df_st['Close'].ewm(span=21).mean()
            df_st['E200'] = df_st['Close'].ewm(span=200).mean()
            
            ltp = float(df_st['Close'].iloc[-1])
            e9, e21, e200 = float(df_st['E9'].iloc[-1]), float(df_st['E21'].iloc[-1]), float(df_st['E200'].iloc[-1])

            # Safety Logic: Check if values are valid numbers
            if not pd.isna(e9) and not pd.isna(e200):
                is_call = bool(e9 > e21 and ltp > e200)
                is_put = bool(e9 < e21 and ltp < e200)

                if is_call and st.session_state.st_last != "CALL":
                    st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
                    jarvis_emergency_system(f"Stock Signal: Call Entry at {ltp}")
                elif is_put and st.session_state.st_last != "PUT":
                    st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
                    jarvis_emergency_system(f"Stock Signal: Put Entry at {ltp}")

                st.metric(f"NSE {asset_st}", f"₹{round(ltp,2)}", delta=st.session_state.st_last)
                fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
                fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_st, use_container_width=True)
        except: st.info("📡 Calibrating Stock Data...")
    else: st.warning("📡 Waiting for NSE Satellite Data...")

# --- ₿ SECTION B: CRYPTO (JARVIS R) ---
with col_cr:
    st.subheader("₿ CRYPTO: HUNTER MODE")
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        res = requests.get(url, timeout=2).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = df_cr['close'].ewm(span=9).mean()
            df_cr['E21'] = df_cr['close'].ewm(span=21).mean()
            df_cr['E200'] = df_cr['close'].ewm(span=200).mean()
            
            ltp_r = float(df_cr['close'].iloc[-1])
            e9_r, e21_r, e200_r = float(df_cr['E9'].iloc[-1]), float(df_cr['E21'].iloc[-1]), float(df_cr['E200'].iloc[-1])

            if e9_r > e21_r and ltp_r > e200_r and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_r
                jarvis_emergency_system("Crypto Alert: Bitcoin Call Buy")
            elif e9_r < e21_r and ltp_r < e200_r and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r
                jarvis_emergency_system("Crypto Alert: Bitcoin Put Buy")

            st.metric("BTC PRICE", f"${ltp_r}", delta=st.session_state.r_last)
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting to Crypto Feed...")

if st.button("🔄 Reset Master"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
