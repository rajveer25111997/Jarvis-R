import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="Jarvis R: Persistent Tracker", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v36_stable")

def jarvis_r_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. DATA ENGINE ---
def get_crypto_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        response = requests.get(url, timeout=3).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return None

st.markdown("<h1 style='text-align:center; color:#FFD700;'>📊 JARVIS-R: PERSISTENT TRACKER v36.0</h1>", unsafe_allow_html=True)

# Persistent States
if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""
if "trade_history" not in st.session_state: st.session_state.trade_history = []
if "win_count" not in st.session_state: st.session_state.win_count = 0
if "loss_count" not in st.session_state: st.session_state.loss_count = 0

df = get_crypto_data()

# --- 🚀 3. THE ENGINE ---
if df is not None and not df.empty:
    # Technicals
    df['EMA9'] = ta.ema(df['close'], length=9)
    df['EMA21'] = ta.ema(df['close'], length=21)
    df['EMA200'] = ta.ema(df['close'], length=200)
    
    ltp = float(df['close'].iloc[-1])
    ema9, ema21, ema200 = df['EMA9'].iloc[-1], df['EMA21'].iloc[-1], df['EMA200'].iloc[-1]

    # Signal Logic
    is_call = bool(ema9 > ema21 and ltp > ema200)
    is_put = bool(ema9 < ema21 and ltp < ema200)

    # 🚦 Handle Active Signal
    if is_call and st.session_state.l_s != "CALL":
        st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
        jarvis_r_speak("New Call Entry Detected")
    elif is_put and st.session_state.l_s != "PUT":
        st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
        jarvis_r_speak("New Put Entry Detected")

    # 📊 Win/Loss Tracking (When Signal Ends)
    if st.session_state.e_p > 0:
        pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2)
        # Reversal condition to close trade
        reversal = (st.session_state.l_s == "CALL" and ema9 < ema21) or (st.session_state.l_s == "PUT" and ema9 > ema21)
        
        if reversal:
            result = "WIN ✅" if pnl > 0 else "LOSS ❌"
            if pnl > 0: st.session_state.win_count += 1
            else: st.session_state.loss_count += 1
            
            st.session_state.trade_history.append({"Type": st.session_state.l_s, "Entry": st.session_state.e_p, "Exit": ltp, "Points": pnl, "Result": result})
            st.session_state.e_p = 0.0; st.session_state.l_s = ""

    # --- 📺 DASHBOARD (Always Visible) ---
    c1, c2, c3, c4 = st.columns(4)
    total = st.session_state.win_count + st.session_state.loss_count
    c1.metric("LIVE BTC", f"${ltp}")
    c2.metric("WINS ✅", st.session_state.win_count)
    c3.metric("LOSS ❌", st.session_state.loss_count)
    acc = round((st.session_state.win_count / total * 100), 1) if total > 0 else 0
    c4.metric("ACCURACY", f"{acc}%")

    # Big Alert (Only if active)
    if st.session_state.l_s != "":
        color = "#1E5631" if st.session_state.l_s == "CALL" else "#800000"
        st.markdown(f"<div style='background-color:{color}; padding:15px; border-radius:10px; text-align:center;'><h2>ACTIVE: {st.session_state.l_s} from {st.session_state.e_p} | PNL: {pnl} Pts</h2></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color:#1B2631; padding:15px; border-radius:10px; text-align:center;'><h3>⌛ Scanning for Next Signal...</h3></div>", unsafe_allow_html=True)

    # Always Show Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange')))
    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Trade History (Always Visible at bottom)
    if st.session_state.trade_history:
        st.subheader("📜 Recent Signal Report")
        st.table(pd.DataFrame(st.session_state.trade_history).tail(5))

else:
    st.info("📡 Connection stable, waiting for first data tick...")

if st.button("🗑️ Clear Tracker Data"):
    st.session_state.trade_history = []; st.session_state.win_count = 0; st.session_state.loss_count = 0
    st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()
