import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="Jarvis R: Pro Station", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v31_reliable") # 2 Sec for stability

def jarvis_r_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. FAST DATA (Requesting more history to fix EMA error) ---
def get_reliable_data():
    # 500 candles requested to ensure EMA200 is always ready
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=500"
    try:
        response = requests.get(url, timeout=5).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return pd.DataFrame()

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛡️ JARVIS-R: PRO-TRADER v31.0</h1>", unsafe_allow_html=True)

if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""

df = get_reliable_data()

# --- 🚀 3. ROBUST EXECUTION ---
if not df.empty and len(df) > 200:
    try:
        df['EMA9'] = ta.ema(df['close'], length=9)
        df['EMA21'] = ta.ema(df['close'], length=21)
        df['EMA200'] = ta.ema(df['close'], length=200)
        
        # Check if EMA calculation is complete
        if df['EMA200'].isnull().iloc[-1]:
            st.info("⌛ Indicators are warming up... fetching more history.")
        else:
            ltp = float(df['close'].iloc[-1])
            ema9, ema21, ema200 = df['EMA9'].iloc[-1], df['EMA21'].iloc[-1], df['EMA200'].iloc[-1]

            # Signal Logic
            is_call = bool(ema9 > ema21 and ltp > ema200)
            is_put = bool(ema9 < ema21 and ltp < ema200)

            # Dashboard Header
            if is_call: 
                st.success(f"🚀 CALL SIGNAL ACTIVE | ENTRY: {ltp}")
                if st.session_state.l_s != "CALL":
                    st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
                    jarvis_r_speak("Rajveer Sir, Call Buy karo")
            elif is_put: 
                st.error(f"📉 PUT SIGNAL ACTIVE | ENTRY: {ltp}")
                if st.session_state.l_s != "PUT":
                    st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
                    jarvis_r_speak("Rajveer Sir, Put Buy karo")

            # Always Show Chart & Price
            c1, c2, c3 = st.columns(3)
            c1.metric("LIVE BITCOIN", f"${ltp}")
            c2.metric("CURRENT STATUS", st.session_state.l_s if st.session_state.l_s else "Scanning...")
            pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2) if st.session_state.e_p > 0 else 0
            c3.metric("LIVE PNL", f"{pnl} Pts")

            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange')))
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("Error in calculations. Auto-recovering...")
else:
    st.warning("📡 Still connecting to Market Satellite... Please stay on this tab.")

if st.button("🔄 Reset Trade State"):
    st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()
