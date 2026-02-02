import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="JARVIS v55: VOICE ENTRY", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v55_voice")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #06090F; }
    .signal-box { padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; }
    .price-display { font-size: 32px; color: #00FFCC; font-weight: bold; font-family: 'Courier New'; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔊 2. VOICE ENGINE (ENTERY PRICE FIXED) ---
def jarvis_speak_entry(text):
    js_code = f"""
    <script>
    if ('wakeLock' in navigator) {{ navigator.wakeLock.request('screen').catch(e => {{}}); }}
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance('{text}');
    msg.lang = 'hi-IN';
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: VOICE PRECISION v55.0</h1>", unsafe_allow_html=True)

if st.button("📢 ACTIVATE VOICE (सिग्नल और एंट्री सुनने के लिए दबाएं)"):
    jarvis_speak_entry("Voice Active. Rajveer Sir, ab main entry price bhi bolkar bataunga.")

# --- 🧠 3. STATE ---
for k in ["st_last", "st_ep", "st_tg", "r_last", "r_ep", "r_tg"]:
    if k not in st.session_state: st.session_state[k] = "" if "last" in k else 0.0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (Entry Voice) ---
with col_st:
    st.markdown("<h2 style='color:#007BFF; text-align:center;'>📈 NSE SIGNAL</h2>", unsafe_allow_html=True)
    asset_st = st.sidebar.selectbox("Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    tk = yf.Ticker(asset_st)
    df_st = tk.history(period="2d", interval="1m")
    
    if not df_st.empty:
        ltp = float(df_st['Close'].iloc[-1])
        e9 = df_st['Close'].ewm(span=9).mean().iloc[-1]
        e21 = df_st['Close'].ewm(span=21).mean().iloc[-1]

        # Signal Logic
        if e9 > e21 and ltp > df_st['Close'].ewm(span=200).mean().iloc[-1] and st.session_state.st_last != "CALL":
            st.session_state.st_last = "CALL"; st.session_state.st_ep = round(ltp, 2)
            st.session_state.st_tg = round(ltp + 50, 2)
            jarvis_speak_entry(f"स्टॉक कॉल बाय! एंट्री प्राइस है {st.session_state.st_ep} और टारगेट है {st.session_state.st_tg}")
        elif e9 < e21 and ltp < df_st['Close'].ewm(span=200).mean().iloc[-1] and st.session_state.st_last != "PUT":
            st.session_state.st_last = "PUT"; st.session_state.st_ep = round(ltp, 2)
            st.session_state.st_tg = round(ltp - 50, 2)
            jarvis_speak_entry(f"स्टॉक पुट बाय! एंट्री प्राइस है {st.session_state.st_ep} और टारगेट है {st.session_state.st_tg}")

        # UI
        bg = "#1E5631" if "CALL" in st.session_state.st_last else "#800000" if "PUT" in st.session_state.st_last else "#1B2631"
        st.markdown(f"<div class='signal-box' style='background-color:{bg};'>SIGNAL: {st.session_state.st_last}</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.markdown(f"**LIVE:** <div class='price-display'>{ltp:.2f}</div>", unsafe_allow_html=True)
        c2.markdown(f"**ENTRY:** <div class='price-display'>{st.session_state.st_ep:.2f}</div>", unsafe_allow_html=True)

        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO (Entry Voice) ---
with col_cr:
    st.markdown("<h2 style='color:#F7931A; text-align:center;'>₿ CRYPTO SIGNAL</h2>", unsafe_allow_html=True)
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=100").json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            ltp_r = float(df_cr['close'].iloc[-1])
            
            if ltp_r > df_cr['close'].ewm(span=9).mean().iloc[-1] and st.session_state.r_last != "CALL":
                st.session_state.r_last = "CALL"; st.session_state.r_ep = round(ltp_r, 2)
                st.session_state.r_tg = round(ltp_r + 200, 2)
                jarvis_speak_entry(f"क्रिप्टो कॉल बाय! एंट्री प्राइस है {st.session_state.r_ep}")
            elif ltp_r < df_cr['close'].ewm(span=9).mean().iloc[-1] and st.session_state.r_last != "PUT":
                st.session_state.r_last = "PUT"; st.session_state.r_ep = round(ltp_r, 2)
                st.session_state.r_tg = round(ltp_r - 200, 2)
                jarvis_speak_entry(f"क्रिप्टो पुट बाय! एंट्री प्राइस है {st.session_state.r_ep}")

            bg_cr = "#1E5631" if "CALL" in st.session_state.r_last else "#800000" if "PUT" in st.session_state.r_last else "#1B2631"
            st.markdown(f"<div class='signal-box' style='background-color:{bg_cr};'>CRYPTO: {st.session_state.r_last}</div>", unsafe_allow_html=True)
            
            d1, d2 = st.columns(2)
            d1.markdown(f"**LIVE:** <div class='price-display'>${ltp_r:.2f}</div>", unsafe_allow_html=True)
            d2.markdown(f"**ENTRY:** <div class='price-display'>${st.session_state.r_ep:.2f}</div>", unsafe_allow_html=True)

            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting...")

if st.button("🔄 Reset Hunter System"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
