import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS ULTIMATE v75", layout="wide")
st_autorefresh(interval=3000, key="jarvis_v75_final_fix")

# --- 🔊 2. VOICE ENGINE (With User Interaction Fix) ---
def jarvis_speak(text):
    if text:
        js = f"""
        <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        msg.rate = 0.9;
        window.speechSynthesis.speak(msg);
        </script>
        """
        st.components.v1.html(js, height=0)

# --- 🧠 3. HARD LOCK STATE ---
if "st_locked" not in st.session_state:
    st.session_state.st_locked = False
if "cr_locked" not in st.session_state:
    st.session_state.cr_locked = False
if "balance" not in st.session_state:
    st.session_state.balance = 120.0

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS DUAL: ULTIMATE v75.0</h1>", unsafe_allow_html=True)

# आवाज़ चालू करने के लिए जरूरी बटन
if st.button("🔊 ACTIVATE JARVIS VOICE (आवाज़ के लिए यहाँ दबाएँ)"):
    jarvis_speak("प्रणाम राजवीर सर, जार्विस वॉइस सिस्टम एक्टिवेट हो गया है")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK ---
with col_st:
    st.header("📈 NSE STOCK")
    asset_st = st.sidebar.selectbox("Asset", ["^NSEI", "^NSEBANK"])
    df_st = yf.Ticker(asset_st).history(period="3d", interval="1m")
    
    if not df_st.empty:
        ltp_st = round(df_st['Close'].iloc[-1], 2)
        df_st['E9'] = ta.ema(df_st['Close'], length=9)
        df_st['E21'] = ta.ema(df_st['Close'], length=21)

        # LOCK LOGIC
        if not st.session_state.st_locked:
            if df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1]:
                st.session_state.st_sig = "CALL"; st.session_state.st_ep = ltp_st
                st.session_state.st_sl = ltp_st - 50; st.session_state.st_tg = ltp_st + 250
                st.session_state.st_locked = True
                jarvis_speak(f"एन एस ई कॉल लॉक्ड")
            elif df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1]:
                st.session_state.st_sig = "PUT"; st.session_state.st_ep = ltp_st
                st.session_state.st_sl = ltp_st + 50; st.session_state.st_tg = ltp_st - 250
                st.session_state.st_locked = True
                jarvis_speak(f"एन एस ई पुट लॉक्ड")

        st.metric(f"{asset_st}", f"₹{ltp_st}")
        st.success(f"📌 {st.session_state.get('st_sig', 'SCANNING')} | Entry: {st.session_state.get('st_ep', 0)} | SL: {st.session_state.get('st_sl', 0)} | TG: {st.session_state.get('st_tg', 0)}")
        
        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO ---
with col_cr:
    st.header("₿ CRYPTO")
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=200"
    res = requests.get(url).json()
    df_cr = pd.DataFrame(res['Data']['Data'])
    
    if not df_cr.empty:
        ltp_cr = float(df_cr['close'].iloc[-1])
        df_cr['E9'] = ta.ema(df_cr['close'], length=9)
        df_cr['E21'] = ta.ema(df_cr['close'], length=21)

        if not st.session_state.cr_locked:
            if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1]:
                st.session_state.cr_sig = "CALL"; st.session_state.cr_ep = ltp_cr
                st.session_state.cr_sl = ltp_cr - 200; st.session_state.cr_tg = ltp_cr + 600
                st.session_state.cr_locked = True
                jarvis_speak("क्रिप्टो कॉल लॉक्ड")
            elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1]:
                st.session_state.cr_sig = "PUT"; st.session_state.cr_ep = ltp_cr
                st.session_state.cr_sl = ltp_cr + 200; st.session_state.cr_tg = ltp_cr - 600
                st.session_state.cr_locked = True
                jarvis_speak("क्रिप्टो पुट लॉक्ड")

        st.metric("BTC/USD", f"${ltp_cr}")
        qty = round((st.session_state.balance * 10) / ltp_cr, 4)
        st.warning(f"💰 Qty: {qty} BTC | Bal: ${st.session_state.balance}")
        st.info(f"📌 {st.session_state.get('cr_sig', 'SCANNING')} | Entry: {st.session_state.get('cr_ep', 0)} | SL: {st.session_state.get('cr_sl', 0)} | TG: {st.session_state.get('cr_tg', 0)}")

# --- 🛡️ UNLOCK BUTTON ---
st.write("---")
if st.button("🔄 UNLOCK ALL & SCAN NEW"):
    st.session_state.st_locked = False
    st.session_state.cr_locked = False
    st.rerun()
