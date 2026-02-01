import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. PRO CONFIG ---
st.set_page_config(page_title="Jarvis R: Supreme Hunter", layout="wide")
st_autorefresh(interval=1500, key="jarvis_v32_supreme")

# --- 🔊 2. SUPREME VOICE ENGINE ---
def jarvis_r_speak(text, alert_type="normal"):
    # normal: सूचना | emergency: सायरन के साथ
    beep = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if alert_type == "normal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js = f"""
    <script>
    window.speechSynthesis.cancel();
    new Audio('{beep}').play();
    var m = new SpeechSynthesisUtterance('{text}');
    m.lang = 'hi-IN'; m.rate = 1.0;
    window.speechSynthesis.speak(m);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🧠 3. HIGH-SPEED DATA ---
def get_reliable_data():
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=500"
    try:
        response = requests.get(url, timeout=5).json()
        df = pd.DataFrame(response['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: return pd.DataFrame()

# --- 🎨 4. INTERFACE ---
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🚀 JARVIS-R: SUPREME HUNTER v32.0</h1>", unsafe_allow_html=True)

if "e_p" not in st.session_state: st.session_state.e_p = 0.0
if "l_s" not in st.session_state: st.session_state.l_s = ""
if "hunter_mode" not in st.session_state: st.session_state.hunter_mode = False

df = get_reliable_data()

# --- 🚀 5. THE HUNTER ENGINE ---
if not df.empty and len(df) > 200:
    try:
        # Technicals
        df['EMA9'] = ta.ema(df['close'], length=9)
        df['EMA21'] = ta.ema(df['close'], length=21)
        df['EMA200'] = ta.ema(df['close'], length=200)
        df.dropna(subset=['EMA200'], inplace=True)
        
        ltp = float(df['close'].iloc[-1])
        ema9 = df['EMA9'].iloc[-1]
        ema21 = df['EMA21'].iloc[-1]
        ema200 = df['EMA200'].iloc[-1]

        # 🚦 Signal Logic (Combined Strength)
        is_call = bool(ema9 > ema21 and ltp > ema200)
        is_put = bool(ema9 < ema21 and ltp < ema200)

        # Voice & State Management
        if is_call and st.session_state.l_s != "CALL":
            st.session_state.l_s = "CALL"; st.session_state.e_p = ltp; st.session_state.hunter_mode = False
            jarvis_r_speak(f"Rajveer Sir, Call Option Buy karo! Entry price hai {ltp}")
        elif is_put and st.session_state.l_s != "PUT":
            st.session_state.l_s = "PUT"; st.session_state.e_p = ltp; st.session_state.hunter_mode = False
            jarvis_r_speak(f"Rajveer Sir, Put Option Buy karo! Entry price hai {ltp}")

        # --- 📺 VISUAL COMMAND DASHBOARD ---
        if st.session_state.l_s != "":
            color = "#1E5631" if st.session_state.l_s == "CALL" else "#800000"
            border = "#00FF00" if st.session_state.l_s == "CALL" else "#FF0000"
            st.markdown(f"""<div style='background-color:{color}; padding:20px; border-radius:15px; text-align:center; border: 4px solid {border};'>
                <h1 style='color:white; margin:0;'>{st.session_state.l_s} OPTION ACTIVE</h1>
                <h2 style='color:yellow; margin:5px;'>ENTRY: ${st.session_state.e_p} | LIVE: ${ltp}</h2>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#1B2631; padding:20px; border-radius:15px; text-align:center;'><h2>⌛ Scanning for 250-500 Point Momentum...</h2></div>", unsafe_allow_html=True)

        # --- 🛡️ HUNTING LOGIC (250, 300, 500 Pts + Trend Follow) ---
        if st.session_state.e_p > 0:
            pnl = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2)
            
            # 1. Momentum Voice Alert
            if pnl >= 250 and not st.session_state.hunter_mode:
                jarvis_r_speak("Rajveer Sir, 250 point paar! Trend bahut majboot hai, ruko nahi!", alert_type="normal")
                st.session_state.hunter_mode = True
            elif pnl >= 500:
                jarvis_r_speak("Jackpot! 500 points pure! Exit karne ka socho!", alert_type="emergency")

            # 2. Trend Reversal Exit (Agar trend ulat jaye)
            reversal = (st.session_state.l_s == "CALL" and ltp < ema9) or (st.session_state.l_s == "PUT" and ltp > ema9)
            if reversal and pnl > 50:
                jarvis_r_speak("Alert! Trend ulat raha hai. Exit! Exit!", alert_type="emergency")
                st.session_state.e_p = 0.0; st.session_state.l_s = "EXIT"

        # --- 📊 METRICS & CHART ---
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("LIVE BTC", f"${ltp}")
        m2.metric("ENTRY PRICE", f"${st.session_state.e_p if st.session_state.e_p > 0 else '---'}")
        pnl_val = round(ltp - st.session_state.e_p if st.session_state.l_s == "CALL" else st.session_state.e_p - ltp, 2) if st.session_state.e_p > 0 else 0
        m3.metric("LIVE PNL (Points)", f"{pnl_val}", delta=pnl_val)

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='orange', width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'], name='Trend (9)', line=dict(color='cyan', width=1)))
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("Restarting Data Satellite... Please wait.")
else:
    st.warning("📡 Connecting... Getting 500 candles for EMA stability.")

if st.button("🔄 Manual Trade Reset"):
    st.session_state.e_p = 0.0; st.session_state.l_s = ""; st.session_state.hunter_mode = False; st.rerun()
