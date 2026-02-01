import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. CONFIG ---
st.set_page_config(page_title="Jarvis R: Visual Sniper", layout="wide")
st_autorefresh(interval=1000, key="jarvis_visual_v28")

# --- 🔊 2. VOICE ENGINE ---
def jarvis_r_speak(text):
    js = f"""
    <script>
    window.speechSynthesis.cancel();
    var m = new SpeechSynthesisUtterance('{text}');
    m.lang = 'hi-IN'; m.rate = 1.0;
    window.speechSynthesis.speak(m);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🧠 3. DATA ENGINE ---
def get_fast_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=300"
    try:
        response = requests.get(url).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return pd.DataFrame()

# --- 🎨 4. BRANDING ---
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🎯 JARVIS-R: VISUAL COMMAND CENTER</h1>", unsafe_allow_html=True)

if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""

# --- 🚀 5. EXECUTION ---
df = get_fast_data()

if not df.empty and len(df) > 200:
    df['EMA9'] = ta.ema(df['close'], length=9)
    df['EMA21'] = ta.ema(df['close'], length=21)
    df['EMA200'] = ta.ema(df['close'].astype(float), length=200)
    adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
    df['ADX'] = adx_df['ADX_14']
    df.dropna(subset=['EMA200'], inplace=True)

    if not df.empty:
        ltp = float(df['close'].iloc[-1])
        cur_adx = float(df['ADX'].iloc[-1])
        
        # --- 🚦 CALL/PUT LOGIC ---
        is_trending = cur_adx > 20
        is_call = bool(is_trending and df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and ltp > df['EMA200'].iloc[-1])
        is_put = bool(is_trending and df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and ltp < df['EMA200'].iloc[-1])

        # Voice Trigger
        if is_call and st.session_state.l_s != "CALL":
            st.session_state.l_s = "CALL"; st.session_state.e_p = ltp
            jarvis_r_speak(f"Rajveer Sir, Call Option Buy karo!")
        elif is_put and st.session_state.l_s != "PUT":
            st.session_state.l_s = "PUT"; st.session_state.e_p = ltp
            jarvis_r_speak(f"Rajveer Sir, Put Option Buy karo!")

        # --- 📺 VISUAL DASHBOARD ---
        # बड़ा सिग्नल कार्ड
        if st.session_state.l_s == "CALL":
            st.markdown(f"""<div style='background-color:#008000; padding:20px; border-radius:10px; text-align:center;'>
                <h1 style='color:white; margin:0;'>🚀 BUY CALL OPTION NOW</h1>
                <h2 style='color:yellow; margin:0;'>ENTRY: ${st.session_state.e_p} | LTP: ${ltp}</h2>
            </div>""", unsafe_allow_html=True)
        elif st.session_state.l_s == "PUT":
            st.markdown(f"""<div style='background-color:#FF0000; padding:20px; border-radius:10px; text-align:center;'>
                <h1 style='color:white; margin:0;'>📉 BUY PUT OPTION NOW</h1>
                <h2 style='color:yellow; margin:0;'>ENTRY: ${st.session_state.e_p} | LTP: ${ltp}</h2>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; padding:10px;'><h3>⌛ Scanning for Master Signal...</h3></div>", unsafe_allow_html=True)

        st.write("---")
        # चार्ट और बाकी मीटर
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.metric("CURRENT ADX (Strength)", round(cur_adx, 2))
            if st.session_state.e_p > 0:
                pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2)
                st.metric("LIVE POINTS", f"{pnl} Pts", delta=pnl)

if st.button("🔄 Reset Manual (Next Trade)"):
    st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.rerun()
