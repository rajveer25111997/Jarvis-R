import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS DUAL: COMPLETE", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v57_reset")

# --- 🔊 2. SIREN & HUNTER VOICE ENGINE ---
def jarvis_emergency_system(text, alert_type="normal"):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(err => {{}}); }}
    window.speechSynthesis.cancel();
    var siren = new Audio('{siren_url}'); siren.play();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN'; msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    }}, 1200);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: NSE STOCK & CRYPTO HUNTER</h1>", unsafe_allow_html=True)

# --- 🧠 3. STATE MANAGEMENT (Dono Markets ke liye) ---
states = {
    "st_last": "", "st_ep": 0.0, "st_sl": 0.0,
    "r_last": "", "r_ep": 0.0, "r_sl": 0.0
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 🚀 4. DUAL SCREEN LAYOUT ---
col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE) ---
with col_st:
    st.subheader("📈 NSE STOCK MARKET")
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    try:
        df_st = yf.download(asset_st, period="5d", interval="1m", progress=False)
        if not df_st.empty and len(df_st) > 100:
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            df_st['E200'] = ta.ema(df_st['Close'], length=200)
            ltp = float(df_st['Close'].iloc[-1])
            
            # Javed Logic
            is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp > df_st['E200'].iloc[-1])
            is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp < df_st['E200'].iloc[-1])

            if is_call and st.session_state.st_last != "CALL":
                st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp; st.session_state.st_sl = ltp - 40
                jarvis_emergency_system(f"Stock Call Entry! Price: {ltp}")
            elif is_put and st.session_state.st_last != "PUT":
                st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp; st.session_state.st_sl = ltp + 40
                jarvis_emergency_system(f"Stock Put Entry! Price: {ltp}")

            # Display Meters
            st.metric(f"NSE {asset_st}", f"₹{round(ltp,2)}", delta=st.session_state.st_last)
            st.info(f"**ENTRY:** {st.session_state.st_ep} | **SL:** {st.session_state.st_sl}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.add_trace(go.Scatter(x=df_st.index, y=df_st['E200'], name='200 EMA', line=dict(color='orange')))
            fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_st, use_container_width=True)
    except: st.info("📡 NSE Data Connecting...")

# --- ₿ SECTION B: CRYPTO MARKET (Jarvis R) ---
with col_cr:
    st.subheader("₿ CRYPTO MARKET")
    try:
        url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
        res = requests.get(url, timeout=3).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)
            df_cr['E200'] = ta.ema(df_cr['close'], length=200)
            ltp_r = float(df_cr['close'].iloc[-1])

            # Crypto Logic
            is_call_r = bool(df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_r > df_cr['E200'].iloc[-1])
            is_put_r = bool(df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_r < df_cr['E200'].iloc[-1])

            if is_call_r and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_r; st.session_state.r_sl = ltp_r - 150
                jarvis_emergency_system("Crypto Call Buy! Bitcoin up.")
            elif is_put_r and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r; st.session_state.r_sl = ltp_r + 150
                jarvis_emergency_system("Crypto Put Buy! Bitcoin down.")

            # Display Meters
            st.metric("BTC PRICE", f"${ltp_r}", delta=st.session_state.r_last)
            st.warning(f"**ENTRY:** {st.session_state.r_ep} | **SL:** {st.session_state.r_sl}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.add_trace(go.Scatter(x=pd.to_datetime(df_cr['time'], unit='s'), y=df_cr['E200'], name='200 EMA', line=dict(color='orange')))
            fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Crypto Data Connecting...")

# --- 🛡️ RESET ---
if st.button("🔄 Reset DUAL Station"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
