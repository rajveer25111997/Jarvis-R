import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG (Stable 2-Sec) ---
st.set_page_config(page_title="JARVIS DUAL v64", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v64_stable")

# --- 🔊 2. ULTIMATE VOICE ENGINE ---
def jarvis_speak_supreme(text):
    js_code = f"""
    <script>
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.lang = 'hi-IN';
    window.speechSynthesis.speak(msg);
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen'); }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🧠 3. STATE MANAGEMENT ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_last": "", "st_ep": 0.0, "st_sl": 0.0,
        "cr_last": "", "cr_ep": 0.0, "cr_sl": 0.0
    })

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL COMMANDER v64.0</h1>", unsafe_allow_html=True)

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE) ---
with col_st:
    st.header("📈 NSE STOCK")
    asset_st = st.selectbox("Select NSE", ["^NSEI", "^NSEBANK"], key="st_box")
    # EMA200 के लिए कम से कम 5 दिन का डेटा ज़रूरी है
    df_st = yf.download(asset_st, period="5d", interval="1m", progress=False)
    
    if not df_st.empty and len(df_st) > 200:
        try:
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            df_st['E200'] = ta.ema(df_st['Close'], length=200)
            
            # --- 🛡️ EROR PROTECTION LAYER ---
            curr_e9 = df_st['E9'].iloc[-1]
            curr_e21 = df_st['E21'].iloc[-1]
            curr_e200 = df_st['E200'].iloc[-1]
            ltp_st = df_st['Close'].iloc[-1]

            # केवल तभी आगे बढ़ें जब सारा डेटा 'Number' हो
            if not pd.isna(curr_e9) and not pd.isna(curr_e200):
                is_call = bool(curr_e9 > curr_e21 and ltp_st > curr_e200)
                is_put = bool(curr_e9 < curr_e21 and ltp_st < curr_e200)

                if is_call and st.session_state.st_last != "CALL":
                    st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp_st
                    st.session_state.st_sl = ltp_st - 40
                    jarvis_speak_supreme(f"निफ़्टी कॉल सिग्नल! एंट्री {round(ltp_st,2)}")
                elif is_put and st.session_state.st_last != "PUT":
                    st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp_st
                    st.session_state.st_sl = ltp_st + 40
                    jarvis_speak_supreme(f"निफ़्टी पुट सिग्नल! एंट्री {round(ltp_st,2)}")

                st.metric(f"NSE {asset_st}", f"₹{round(ltp_st,2)}", delta=st.session_state.st_last)
                st.write(f"**Entry:** {st.session_state.st_ep} | **SL:** {st.session_state.st_sl}")
                
                fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
                fig_st.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_st, use_container_width=True)
        except: st.info("📡 NSE डेटा प्रोसेस हो रहा है...")
    else: st.warning("📡 NSE डेटा सिंक हो रहा है... इंतज़ार करें।")

# --- ₿ SECTION B: CRYPTO MARKET (Jarvis R) ---
with col_cr:
    st.header("₿ CRYPTO MARKET")
    try:
        url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
        res = requests.get(url, timeout=3).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)
            df_cr['E200'] = ta.ema(df_cr['close'], length=200)
            ltp_cr = float(df_cr['close'].iloc[-1])

            # Safety Check for Crypto
            if not pd.isna(df_cr['E9'].iloc[-1]):
                if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1] and ltp_cr > df_cr['E200'].iloc[-1] and st.session_state.cr_last != "CALL":
                    st.session_state.cr_last = "CALL"; st.session_state.cr_ep = ltp_cr; st.session_state.cr_sl = ltp_cr - 150
                    jarvis_speak_supreme("क्रिप्टो कॉल एंट्री!")
                elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1] and ltp_cr < df_cr['E200'].iloc[-1] and st.session_state.cr_last != "PUT":
                    st.session_state.cr_last = "PUT"; st.session_state.cr_ep = ltp_cr; st.session_state.cr_sl = ltp_cr + 150
                    jarvis_speak_supreme("क्रिप्टो पुट एंट्री!")

            st.metric("BTC PRICE", f"${ltp_cr}", delta=st.session_state.cr_last)
            st.write(f"**Entry:** {st.session_state.cr_ep} | **SL:** {st.session_state.cr_sl}")
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 क्रिप्टो डेटा सिंक हो रहा है...")

# --- 🛡️ FULL RESET ---
if st.button("🔄 Full Reset Master System"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
