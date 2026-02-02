import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS (1-SEC) ---
st.set_page_config(page_title="JARVIS v48: FINAL MASTER", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v48_fix")

# --- 🔊 2. EMERGENCY VOICE & WAKE ENGINE ---
def jarvis_emergency_system(text, alert_type="normal"):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(err => {{}}); }}
    var siren = new Audio('{siren_url}');
    siren.play();
    window.speechSynthesis.cancel();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        window.speechSynthesis.speak(msg);
    }}, 1000);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🚀 JARVIS DUAL: MASTER COMMANDER v48.0</h1>", unsafe_allow_html=True)

if st.button("📢 ACTIVATE JARVIS SYSTEM (Voice & Siren Active)"):
    jarvis_emergency_system("System Online Rajveer Sir. Trading Station Ready.")

# --- 🧠 3. STATE MANAGEMENT ---
keys = ["st_last", "st_ep", "st_sl", "st_tg", "r_last", "r_ep", "r_sl", "r_tg"]
for k in keys:
    if k not in st.session_state: st.session_state[k] = "" if "last" in k else 0.0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK MARKET ---
with col_st:
    st.markdown("<h2 style='color:#007BFF;'>📈 NSE STATION</h2>", unsafe_allow_html=True)
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    
    # Chart aur Data Fix
    df_st = yf.download(asset_st, period="5d", interval="1m", progress=False)
    
    if not df_st.empty and len(df_st) > 20:
        df_st['E9'] = df_st['Close'].ewm(span=9).mean()
        df_st['E21'] = df_st['Close'].ewm(span=21).mean()
        df_st['E200'] = df_st['Close'].ewm(span=200).mean()
        
        ltp = float(df_st['Close'].iloc[-1])
        e9, e21, e200 = df_st['E9'].iloc[-1], df_st['E21'].iloc[-1], df_st['E200'].iloc[-1]
        
        # Exact Strike Price
        strike = round(ltp / 50 if "NSEI" in asset_st else ltp / 100) * (50 if "NSEI" in asset_st else 100)

        # Signal Logic
        is_call = e9 > e21 and ltp > e200
        is_put = e9 < e21 and ltp < e200

        if is_call and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
            st.session_state.st_sl = ltp - (ltp * 0.002); st.session_state.st_tg = ltp + (ltp * 0.005)
            jarvis_emergency_system(f"Stock Alert! {asset_st} me Call signal. Strike {strike} CE.")
        elif is_put and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
            st.session_state.st_sl = ltp + (ltp * 0.002); st.session_state.st_tg = ltp - (ltp * 0.005)
            jarvis_emergency_system(f"Stock Alert! {asset_st} me Put signal. Strike {strike} PE.")

        # Display Stats
        st.success(f"**SIGNAL:** {st.session_state.st_last} | **STRIKE:** {strike}")
        m1, m2, m3 = st.columns(3)
        m1.metric("LTP", f"₹{round(ltp,2)}")
        m2.metric("TARGET", f"₹{round(st.session_state.st_tg,2)}", delta="High", delta_color="normal")
        m3.metric("STOPLOSS", f"₹{round(st.session_state.st_sl,2)}", delta="Low", delta_color="inverse")

        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.add_trace(go.Scatter(x=df_st.index, y=df_st['E200'], name='200 EMA', line=dict(color='orange')))
        fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_st, use_container_width=True)
    else: st.info("📡 Connecting NSE Feed...")

# --- ₿ SECTION B: CRYPTO MASTER ---
with col_cr:
    st.markdown("<h2 style='color:#F7931A;'>₿ CRYPTO MASTER</h2>", unsafe_allow_html=True)
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        res = requests.get(url, timeout=2).json()
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

            st.info(f"**SIGNAL:** {st.session_state.r_last}")
            c1, c2, c3 = st.columns(3)
            c1.metric("BTC PRICE", f"${ltp_r}")
            c2.metric("TARGET", f"${round(st.session_state.r_tg,1)}")
            c3.metric("SL", f"${round(st.session_state.r_sl,1)}")

            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting Crypto...")

if st.button("🔄 Reset Master System"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
