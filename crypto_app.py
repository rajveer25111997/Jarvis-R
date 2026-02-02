import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="Jarvis v81: Expert Trader", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v81_live")

def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 2. STATE MANAGEMENT ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_locked": False, "st_sig": "WAIT", "st_ep": 0, "st_sl": 0, "st_tg": 0,
        "cr_locked": False, "cr_sig": "WAIT", "cr_ep": 0, "cr_sl": 0, "cr_tg": 0,
        "balance": 120.0 
    })

st.markdown("<h1 style='text-align:center; color:#00FFFF;'>🛡️ JARVIS DUAL: EXPERT TRADER v81.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS VOICE"):
    jarvis_speak("प्रणाम राजवीर सर, वॉइस सिस्टम चालू है")

col1, col2 = st.columns(2)

# --- ₿ SECTION: CRYPTO LIVE (FASTEST DATA) ---
with col1:
    st.header("₿ CRYPTO LIVE")
    try:
        # Using Binance API for Real-time speed
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
        data = requests.get(url).json()
        df = pd.DataFrame(data, columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qa', 'nt', 'tb', 'tq', 'i'])
        df['close'] = df['close'].astype(float)
        ltp = df['close'].iloc[-1]
        
        df['E9'] = ta.ema(df['close'], length=9)
        df['E21'] = ta.ema(df['close'], length=21)

        # 1. CHECK FOR EXIT (TARGET HIT)
        if st.session_state.cr_locked:
            if (st.session_state.cr_sig == "CALL" and ltp >= st.session_state.cr_tg) or \
               (st.session_state.cr_sig == "PUT" and ltp <= st.session_state.cr_tg):
                jarvis_speak("EXIT! EXIT! TARGET ACHIEVED! राजवीर सर बाहर निकलिए")
                st.session_state.cr_locked = False # Auto unlock for new signal
            elif (st.session_state.cr_sig == "CALL" and ltp <= st.session_state.cr_sl) or \
                 (st.session_state.cr_sig == "PUT" and ltp >= st.session_state.cr_sl):
                jarvis_speak("STOP LOSS HIT! EXIT NOW")
                st.session_state.cr_locked = False

        # 2. SCAN FOR NEW SIGNAL
        if not st.session_state.cr_locked:
            if df['E9'].iloc[-1] > df['E21'].iloc[-1]:
                st.session_state.update({"cr_sig": "CALL", "cr_ep": ltp, "cr_sl": ltp-200, "cr_tg": ltp+500, "cr_locked": True})
                jarvis_speak("क्रिप्टो कॉल सिग्नल लॉक्ड! टारगेट पाँच सौ पॉइंट")
            elif df['E9'].iloc[-1] < df['E21'].iloc[-1]:
                st.session_state.update({"cr_sig": "PUT", "cr_ep": ltp, "cr_sl": ltp+200, "cr_tg": ltp-500, "cr_locked": True})
                jarvis_speak("क्रिप्टो पुट सिग्नल लॉक्ड! टारगेट पाँच सौ पॉइंट")

        st.metric("BTC/USDT", f"${ltp}", delta=st.session_state.cr_sig)
        st.info(f"📌 {st.session_state.cr_sig} | ENTRY: {st.session_state.cr_ep} | SL: {st.session_state.cr_sl} | TARGET: {st.session_state.cr_tg}")
        
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    except: st.info("Crypto Loading...")

with col2:
    st.header("📈 NSE LIVE")
    st.info("NSE के लिए GitHub पर yfinance अपडेट करें। ऊपर वाला क्रिप्टो लाइव देखें।")

if st.button("🔄 FORCE RESET"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
