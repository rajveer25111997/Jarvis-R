import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG (Stable 2-Sec) ---
st.set_page_config(page_title="JARVIS DUAL: PROTECTOR", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v58_stable")

# --- 🔊 2. EMERGENCY SIREN & WAKE SYSTEM ---
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

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛰️ JARVIS DUAL: SUPREME PROTECTOR v58.0</h1>", unsafe_allow_html=True)

# --- 🧠 3. STATE MANAGEMENT (All 43+ Points) ---
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.st_last = ""; st.session_state.st_ep = 0.0; st.session_state.st_sl = 0.0; st.session_state.st_tg = 0.0
    st.session_state.r_last = ""; st.session_state.r_ep = 0.0; st.session_state.r_sl = 0.0; st.session_state.r_tg = 0.0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (JAVED & KARISHMA) ---
with col_st:
    st.subheader("📈 NSE STOCK MARKET")
    asset_st = st.sidebar.selectbox("Select NSE", ["^NSEI", "^NSEBANK"], key="st_box")
    try:
        # 7 दिन का डेटा ताकि EMA200 कभी क्रैश न हो
        df_st = yf.download(asset_st, period="7d", interval="1m", progress=False)
        if not df_st.empty and len(df_st) > 200:
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            df_st['E200'] = ta.ema(df_st['Close'], length=200)
            ltp = float(df_st['Close'].iloc[-1])
            
            # Javed Strategy
            is_call = bool(df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp > df_st['E200'].iloc[-1])
            is_put = bool(df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp < df_st['E200'].iloc[-1])

            if is_call and st.session_state.st_last != "CALL":
                st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
                st.session_state.st_sl = ltp - 45; st.session_state.st_tg = ltp + 120
                jarvis_emergency_system(f"Stock Call Entry! Price: {ltp}")
            elif is_put and st.session_state.st_last != "PUT":
                st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
                st.session_state.st_sl = ltp + 45; st.session_state.st_tg = ltp - 120
                jarvis_emergency_system(f"Stock Put Entry! Price: {ltp}")

            # Karishma SL Protection
            if st.session_state.st_ep > 0:
                pnl = ltp - st.session_state.st_ep if st.session_state.st_last == "CALL" else st.session_state.st_ep - ltp
                if pnl <= -45: # Karishma SL
                    jarvis_emergency_system("Karishma SL Hit! Exit Stock.", "emergency")
                    st.session_state.st_last = "EXITED"; st.session_state.st_ep = 0

            st.metric(f"NSE {asset_st}", f"₹{round(ltp,2)}", delta=f"{st.session_state.st_last}")
            st.info(f"**ENTRY:** {st.session_state.st_ep} | **SL:** {st.session_state.st_sl} | **TG:** {st.session_state.st_tg}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.add_trace(go.Scatter(x=df_st.index, y=df_st['E200'], name='200 EMA', line=dict(color='orange')))
            fig_st.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_st, use_container_width=True)
        else: st.warning("📡 NSE Data Re-connecting...")
    except: st.info("📡 Calibrating Stock Satellite...")

# --- ₿ SECTION B: CRYPTO (JARVIS R) ---
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

            if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_r > df_cr['E200'].iloc[-1] and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_r; st.session_state.r_sl = ltp_r - 180
                jarvis_emergency_system("Crypto Call Buy!")
            elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_r < df_cr['E200'].iloc[-1] and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r; st.session_state.r_sl = ltp_r + 180
                jarvis_emergency_system("Crypto Put Buy!")

            # Hunter Momentum Tracker
            if st.session_state.r_ep > 0:
                pnl_r = ltp_r - st.session_state.r_ep if st.session_state.r_last == "CALL" else st.session_state.r_ep - ltp_r
                if pnl_r >= 350: jarvis_emergency_system("Rajveer Sir, Jackpot Points! Ruko nahi!", "normal")

            st.metric("BTC PRICE", f"${ltp_r}", delta=f"{st.session_state.r_last}")
            st.warning(f"**ENTRY:** {st.session_state.r_ep} | **SL:** {st.session_state.r_sl}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.add_trace(go.Scatter(x=pd.to_datetime(df_cr['time'], unit='s'), y=df_cr['E200'], name='200 EMA', line=dict(color='orange')))
            fig_cr.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting Crypto Satellite...")

if st.button("🔄 FULL SYSTEM RECOVERY (RESET)"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
