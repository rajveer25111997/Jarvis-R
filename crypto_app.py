import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="Jarvis R: Performance Tracker", layout="wide")
st_autorefresh(interval=2000, key="jarvis_v35_tracker")

def jarvis_r_speak(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. DATA ENGINE ---
def get_crypto_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        response = requests.get(url, timeout=2).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return None

st.markdown("<h1 style='text-align:center; color:#FFD700;'>📊 JARVIS-R: PERFORMANCE TRACKER</h1>", unsafe_allow_html=True)

# Persistent States for Tracking
if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""
if "total_trades" not in st.session_state: st.session_state.total_trades = 0
if "win_count" not in st.session_state: st.session_state.win_count = 0
if "loss_count" not in st.session_state: st.session_state.loss_count = 0
if "trade_history" not in st.session_state: st.session_state.trade_history = []

df = get_crypto_data()

if df is not None and not df.empty:
    df['EMA9'] = ta.ema(df['close'], length=9)
    df['EMA21'] = ta.ema(df['close'], length=21)
    df['EMA200'] = ta.ema(df['close'], length=200)
    
    ltp = float(df['close'].iloc[-1])
    
    # --- 🚦 SIGNAL LOGIC ---
    is_call = bool(df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and ltp > df['EMA200'].iloc[-1])
    is_put = bool(df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and ltp < df['EMA200'].iloc[-1])

    # NEW TRADE DETECTION
    if is_call and st.session_state.l_s != "CALL":
        st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
        st.session_state.total_trades += 1
        jarvis_r_speak("New Call Signal Detected")
    elif is_put and st.session_state.l_s != "PUT":
        st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
        st.session_state.total_trades += 1
        jarvis_r_speak("New Put Signal Detected")

    # --- 📊 ACCURACY TRACKING (When Signal Changes) ---
    if st.session_state.e_p > 0:
        pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2)
        
        # Check for Reversal to close trade and count win/loss
        rev = (st.session_state.l_s == "CALL" and df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1]) or \
              (st.session_state.l_s == "PUT" and df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1])
        
        if rev:
            status = "WIN ✅" if pnl > 0 else "LOSS ❌"
            if pnl > 0: st.session_state.win_count += 1
            else: st.session_state.loss_count += 1
            
            # Save to history
            st.session_state.trade_history.append({"Type": st.session_state.l_s, "Entry": st.session_state.e_p, "Exit": ltp, "Points": pnl, "Result": status})
            st.session_state.e_p = 0.0; st.session_state.l_s = ""

    # --- 📺 SCOREBOARD DASHBOARD ---
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("TOTAL SIGNALS", st.session_state.total_trades)
    sc2.metric("SUCCESS (WINS)", st.session_state.win_count, delta_color="normal")
    sc3.metric("FAILURES (LOSS)", st.session_state.loss_count, delta_color="inverse")
    accuracy = (st.session_state.win_count / st.session_state.total_trades * 100) if st.session_state.total_trades > 0 else 0
    sc4.metric("ACCURACY %", f"{round(accuracy, 2)}%")

    st.write("---")
    
    # Live Signal Info
    if st.session_state.l_s != "":
        st.info(f"LIVE TRADE: {st.session_state.l_s} from {st.session_state.e_p} | Current PNL: {pnl} Pts")

    # Trade History Table
    if st.session_state.trade_history:
        st.subheader("📜 Recent Signal Report")
        st.table(pd.DataFrame(st.session_state.trade_history).tail(5))

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange')))
    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

if st.button("🗑️ Clear All History"):
    st.session_state.total_trades = 0; st.session_state.win_count = 0; st.session_state.loss_count = 0
    st.session_state.trade_history = []; st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()
