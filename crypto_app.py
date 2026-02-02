import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIG ---
st.set_page_config(page_title="JARVIS DUAL: PROTECTOR", layout="wide")
st_autorefresh(interval=1000, key="jarvis_v47_final")

# --- 🔊 2. EMERGENCY VOICE & WAKE ENGINE ---
def jarvis_emergency_system(text, alert_type="normal"):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-09.mp3" if alert_type == "emergency" else "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
    # JS to keep screen awake and play sound even if locked
    js_code = f"""
    <script>
    // Wake Lock: Screen ko sone nahi dega
    if ('wakeLock' in navigator) {{
        navigator.wakeLock.request('screen').catch(err => {{}});
    }}
    
    // Play Siren
    var siren = new Audio('{siren_url}');
    siren.play();

    // Voice Output
    window.speechSynthesis.cancel();
    setTimeout(function() {{
        var msg = new SpeechSynthesisUtterance('{text}');
        msg.lang = 'hi-IN';
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    }}, 1000);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🎨 3. UI BRANDING ---
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🛰️ JARVIS DUAL: COMMAND CENTER</h1>", unsafe_allow_html=True)

if st.button("📢 ACTIVATE ALARM SYSTEM (इसे पहले दबाएं ताकि लॉक होने पर आवाज़ आए)"):
    jarvis_emergency_system("Alarm System Activated. Rajveer Sir, ab screen lock hone par bhi main bolunga.")

# State Management
for key in ["st_last", "st_ep", "r_last", "r_ep"]:
    if key not in st.session_state: st.session_state[key] = "" if "last" in key else 0.0

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: STOCK MARKET (NSE) ---
with col_st:
    st.markdown("<h2 style='color:#007BFF;'>📈 NSE STOCK MASTER</h2>", unsafe_allow_html=True)
    asset_st = st.sidebar.selectbox("NSE Asset", ["^NSEI", "^NSEBANK"], key="st_box")
    df_st = yf.download(asset_st, period="5d", interval="1m", progress=False)
    
    if not df_st.empty and len(df_st) > 200:
        df_st['E9'] = df_st['Close'].ewm(span=9).mean()
        df_st['E21'] = df_st['Close'].ewm(span=21).mean()
        df_st['E200'] = df_st['Close'].ewm(span=200).mean()
        ltp = float(df_st['Close'].iloc[-1])
        e9, e200 = float(df_st['E9'].iloc[-1]), float(df_st['E200'].iloc[-1])

        # Signal Logic
        is_call = bool(e9 > float(df_st['E21'].iloc[-1]) and ltp > e200)
        is_put = bool(e9 < float(df_st['E21'].iloc[-1]) and ltp < e200)

        # SEPARATE SIGNAL BOX (STOCK)
        if is_call:
            st.markdown("<div style='background-color:#1E5631; padding:20px; border-radius:10px; border:3px solid #00FF00; text-align:center;'><h1 style='color:white; margin:0;'>🚀 CALL BUY NOW</h1></div>", unsafe_allow_html=True)
            if st.session_state.st_last != "CALL":
                st.session_state.st_last = "CALL"; st.session_state.st_ep = ltp
                jarvis_emergency_system(f"Stock Alert! {asset_st} me Call signal.")
        elif is_put:
            st.markdown("<div style='background-color:#800000; padding:20px; border-radius:10px; border:3px solid #FF0000; text-align:center;'><h1 style='color:white; margin:0;'>📉 PUT BUY NOW</h1></div>", unsafe_allow_html=True)
            if st.session_state.st_last != "PUT":
                st.session_state.st_last = "PUT"; st.session_state.st_ep = ltp
                jarvis_emergency_system(f"Stock Alert! {asset_st} me Put signal.")
        else:
            st.info("⌛ NSE SCANNING...")

        st.metric(f"NSE {asset_st}", f"₹{ltp}")
        fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
        fig_st.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)

# --- ₿ SECTION B: CRYPTO (JARVIS R) ---
with col_cr:
    st.markdown("<h2 style='color:#F7931A;'>₿ CRYPTO MASTER</h2>", unsafe_allow_html=True)
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        res = requests.get(url, timeout=2).json()
        df_cr = pd.DataFrame(res['Data']['Data'])
        if not df_cr.empty:
            df_cr['E9'] = df_cr['close'].ewm(span=9).mean()
            df_cr['E21'] = df_cr['close'].ewm(span=21).mean()
            df_cr['E200'] = df_cr['close'].ewm(span=200).mean()
            ltp_r = float(df_cr['close'].iloc[-1])
            e9_r, e200_r = float(df_cr['E9'].iloc[-1]), float(df_cr['E200'].iloc[-1])

            # SEPARATE SIGNAL BOX (CRYPTO)
            if e9_r > float(df_cr['E21'].iloc[-1]) and ltp_r > e200_r:
                st.markdown("<div style='background-color:#1E5631; padding:20px; border-radius:10px; border:3px solid #00FF00; text-align:center;'><h1 style='color:white; margin:0;'>🚀 CALL BUY NOW</h1></div>", unsafe_allow_html=True)
                if st.session_state.r_last != "CALL":
                    st.session_state.r_last = "CALL"; st.session_state.r_ep = ltp_r
                    jarvis_emergency_system("Crypto Alert! Bitcoin me Call buy karo.")
            elif e9_r < float(df_cr['E21'].iloc[-1]) and ltp_r < e200_r:
                st.markdown("<div style='background-color:#800000; padding:20px; border-radius:10px; border:3px solid #FF0000; text-align:center;'><h1 style='color:white; margin:0;'>📉 PUT BUY NOW</h1></div>", unsafe_allow_html=True)
                if st.session_state.r_last != "PUT":
                    st.session_state.r_last = "PUT"; st.session_state.r_ep = ltp_r
                    jarvis_emergency_system("Crypto Alert! Bitcoin me Put buy karo.")
            else:
                st.info("⌛ CRYPTO SCANNING...")

            st.metric("BTC PRICE", f"${ltp_r}")
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=350, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("📡 Connecting Crypto...")

st.write("---")
if st.button("🔄 Reset Master"):
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()
