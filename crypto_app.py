import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SETTINGS ---
st.set_page_config(page_title="JARVIS v52: STABLE", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v52_stable")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .price-box { background-color: #111; padding: 15px; border-radius: 8px; border: 1px solid #333; text-align: center; }
    .label { color: #888; font-size: 12px; }
    .value { color: #00FFCC; font-size: 26px; font-weight: bold; }
    .signal-box { background-color: #1B2631; padding: 10px; border-radius: 5px; text-align: center; border: 2px solid #FFD700; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

def jarvis_emergency_system(text):
    js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang = 'hi-IN'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 🧠 2. PERSISTENT STATE ---
keys = ["st_last", "st_ep", "st_tg", "st_sl", "st_strike", "r_last", "r_ep"]
for k in keys:
    if k not in st.session_state: st.session_state[k] = "" if "last" in k else 0.0

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: STABLE COMMANDER v52.0</h1>", unsafe_allow_html=True)

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK MARKET ---
with col_st:
    st.markdown("<h2 style='color:#007BFF; text-align:center;'>📈 NSE STATION</h2>", unsafe_allow_html=True)
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    tk = yf.Ticker(asset_st)
    df_st = tk.history(period="2d", interval="1m")
    
    if not df_st.empty:
        ltp = float(df_st['Close'].iloc[-1])
        df_st['E9'] = df_st['Close'].ewm(span=9).mean()
        df_st['E21'] = df_st['Close'].ewm(span=21).mean()
        df_st['E200'] = df_st['Close'].ewm(span=200).mean()
        
        # 🎯 STRIKE PRICE LOCK LOGIC (बार-बार बदलने से रोकने के लिए)
        new_strike = round(ltp / 50 if "NSEI" in asset_st else ltp / 100) * (50 if "NSEI" in asset_st else 100)
        if st.session_state.st_strike == 0 or abs(ltp - st.session_state.st_strike) > 25:
            st.session_state.st_strike = new_strike

        # Signal Logic
        is_call = df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp > df_st['E200'].iloc[-1]
        is_put = df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp < df_st['E200'].iloc[-1]

        if is_call and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
            st.session_state.st_tg = ltp + 60; st.session_state.st_sl = ltp - 30
            jarvis_emergency_system(f"Stock Alert: Call Signal. Strike {st.session_state.st_strike}")
        elif is_put and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
            st.session_state.st_tg = ltp - 60; st.session_state.st_sl = ltp + 30
            jarvis_emergency_system(f"Stock Alert: Put Signal. Strike {st.session_state.st_strike}")

        # UI
        st.markdown(f"<div class='signal-box'><b>SIGNAL: {st.session_state.st_last} | ATM STRIKE: {st.session_state.st_strike}</b></div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='price-box'><div class='label'>LIVE</div><div class='value'>{ltp:.2f}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='price-box'><div class='label'>ENTRY</div><div class='value'>{st.session_state.st_ep:.2f}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='price-box'><div class='label'>TARGET</div><div class='value'>{st.session_state.st_tg:.2f}</div></div>", unsafe_allow_html=True)

        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO MASTER ---
with col_cr:
    st.markdown("<h2 style='color:#F7931A; text-align:center;'>₿ CRYPTO MASTER</h2>", unsafe_allow_html=True)
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300").json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            ltp_r = float(df_cr['close'].iloc[-1])
            st.markdown(f"<div class='signal-box'><b>SIGNAL: {st.session_state.r_last}</b></div>", unsafe_allow_html=True)
            
            r1, r2, r3 = st.columns(3)
            with r1: st.markdown(f"<div class='price-box'><div class='label'>BTC LIVE</div><div class='value'>${ltp_r:.2f}</div></div>", unsafe_allow_html=True)
            with r2: st.markdown(f"<div class='price-box'><div class='label'>ENTRY</div><div class='value'>${st.session_state.r_ep:.2f}</div></div>", unsafe_allow_html=True)
            with r3: st.markdown(f"<div class='price-box'><div class='label'>STATUS</div><div class='value'>ACTIVE</div></div>", unsafe_allow_html=True)

            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting...")

if st.button("🔄 Reset Terminal"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
