import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS MASTER v100", layout="wide")
st_autorefresh(interval=3000, key="jarvis_final_v100")

# --- 🔊 2. VOICE ENGINE (Permanent Fix) ---
def jarvis_speak(text):
    if text:
        js = f"""<script>
        window.speechSynthesis.cancel();
        var m = new SpeechSynthesisUtterance('{text}');
        m.lang = 'hi-IN'; m.rate = 1.0;
        window.speechSynthesis.speak(m);
        </script>"""
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT STATE MANAGEMENT (Locking System) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_lock": False, "cr_lock": False, 
        "st_sig": "SCANNING", "cr_sig": "SCANNING",
        "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0,
        "cr_ep": 0.0, "cr_sl": 0.0, "cr_tg": 0.0,
        "balance": 120.0 # $120 for Delta/Crypto
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏛️ JARVIS MASTER COMMANDER v100.0</h1>", unsafe_allow_html=True)

# Important for Voice
if st.button("🔊 ACTIVATE JARVIS VOICE"):
    jarvis_speak("Namaste Rajveer Sir, Jarvis Final Master System taiyar hai.")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (Javed/Karishma Logic) ---
with col_st:
    st.header("📈 NSE STOCK MARKET")
    asset_st = st.sidebar.selectbox("Select Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    try:
        df_st = yf.download(asset_st, period="3d", interval="1m", progress=False)
        if not df_st.empty:
            ltp_st = round(df_st['Close'].iloc[-1], 2)
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            
            # --- LOCKING LOGIC ---
            if not st.session_state.st_lock:
                if df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp_st, "st_sl": ltp_st-50, "st_tg": ltp_st+250, "st_lock": True})
                    jarvis_speak("NSE Call Signal Locked")
                elif df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp_st, "st_sl": ltp_st+50, "st_tg": ltp_st-250, "st_lock": True})
                    jarvis_speak("NSE Put Signal Locked")

            st.metric(f"{asset_st} LIVE", f"₹{ltp_st}")
            st.success(f"📌 {st.session_state.st_sig} | ENTRY: {st.session_state.st_ep} | SL: {st.session_state.st_sl} | TG: {st.session_state.st_tg}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_st, use_container_width=True)
    except: st.info("NSE Data Loading...")

# --- ₿ SECTION B: CRYPTO (Delta Specialist Logic) ---
with col_cr:
    st.header("₿ CRYPTO (BTC/USD)")
    try:
        url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=200"
        res = requests.get(url).json()
        if 'Data' in res:
            df_cr = pd.DataFrame(res['Data']['Data'])
            ltp_cr = float(df_cr['close'].iloc[-1])
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)

            # --- LOCKING LOGIC ---
            if not st.session_state.cr_lock:
                if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1]:
                    st.session_state.update({"cr_sig": "CALL", "cr_ep": ltp_cr, "cr_sl": ltp_cr-200, "cr_tg": ltp_cr+600, "cr_lock": True})
                    jarvis_speak("Crypto Call Signal Locked")
                elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1]:
                    st.session_state.update({"cr_sig": "PUT", "cr_ep": ltp_cr, "cr_sl": ltp_cr+200, "cr_tg": ltp_cr-600, "cr_lock": True})
                    jarvis_speak("Crypto Put Signal Locked")

            st.metric("BTC PRICE", f"${ltp_cr}")
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Qty: {qty} BTC | Capital: $120 (10x)")
            st.info(f"📌 {st.session_state.cr_sig} | ENTRY: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl} | TG: {st.session_state.cr_tg}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("Crypto Data Loading...")

# --- 🛡️ THE MASTER UNLOCK BUTTON ---
st.write("---")
if st.button("🔄 CLEAR ALL & START NEW SCAN"):
    for key in ["st_lock", "cr_lock", "st_sig", "cr_sig", "st_ep", "st_sl", "st_tg", "cr_ep", "cr_sl", "cr_tg"]:
        if key in st.session_state: del st.session_state[key]
    st.rerun()
