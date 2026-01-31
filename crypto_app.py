import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. ULTIMATE CONFIGURATION ---
st.set_page_config(page_title="JARVIS-R: MASTER SNIPER", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_v12_fixed")

# --- 🧠 2. LIGHTNING-FAST DATA ENGINE ---
def get_live_data(coin="BTC"):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={coin}&tsym=USD&limit=100"
    try:
        response = requests.get(url).json()
        data = response['Data']['Data']
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    except: 
        return pd.DataFrame()

# --- 🔊 3. BACKGROUND VOICE & SIREN SYSTEM ---
def jarvis_alert(text, alert_type="signal"):
    siren_url = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if alert_type=="signal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js_code = f"""
    <script>
    var audio = new Audio('{siren_url}');
    audio.play();
    var msg = new SpeechSynthesisUtterance('{text}');
    msg.rate = 1.0; msg.pitch = 1.0; msg.lang = 'hi-IN';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 🏦 4. BRANDING & UI ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #000, #ff4b4b); padding:15px; border-radius:15px; border:2px solid #fff;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: MASTER SNIPER v12.0</h1>
        <p style='color:white; margin:0;'>₹5,000 CAPITAL GUARD | 200-300 PT HUNTER | DISCIPLINE MODE</p>
    </div>
""", unsafe_allow_html=True)

st.write("")
if st.button("📢 ACTIVATE JARVIS VOICE (ट्रेड शुरू करने से पहले इसे एक बार दबाएं)", use_container_width=True):
    jarvis_alert("Jarvis is online. Rajveer Sir, discipline ke saath hunting shuru karte hain.")
    st.success("Jarvis Voice Activated! ✅")

# State Management
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0
if "target_hit" not in st.session_state: st.session_state.target_hit = False

# --- 🚀 5. MASTER EXECUTION ENGINE ---
df = get_live_data("BTC")

if not df.empty:
    ltp = round(df['close'].iloc[-1], 2)
    df['E9'] = df['close'].ewm(span=9).mean()
    df['E21'] = df['close'].ewm(span=21).mean()
    df['E200'] = df['close'].ewm(span=200).mean()

    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    # --- 🚦 SIGNAL TRIGGERS ---
    if buy_sig and st.session_state.last_sig != "BUY" and not st.session_state.target_hit:
        st.session_state.last_sig = "BUY"
        st.session_state.entry = ltp
        jarvis_alert(f"Rajveer Sir, Master Buy Entry at {ltp}. Target 300 points.")

    elif sell_sig and st.session_state.last_sig != "SELL" and not st.session_state.target_hit:
        st.session_state.last_sig = "SELL"
        st.session_state.entry = ltp
        jarvis_alert(f"Rajveer Sir, High Volume Put Entry at {ltp}. Target 300 points.")

    # --- 🎯 ANTI-GREED & SL LOGIC ---
    if st.session_state.entry > 0:
        pnl_pts = round(abs(ltp - st.session_state.entry), 2)
        
        if pnl_pts >= 250 and not st.session_state.target_hit:
            st.session_state.target_hit = True
            jarvis_alert("Rajveer Sir, target achieved! Ab ruko nahi, turant profit lekar nikal jao!", type="exit")

        sl_limit = st.session_state.entry * 0.003
        if (st.session_state.last_sig == "BUY" and ltp < (st.session_state.entry - sl_limit)) or \
           (st.session_state.last_sig == "SELL" and ltp > (st.session_state.entry + sl_limit)):
            if not st.session_state.target_hit:
                st.session_state.entry = 0
                st.session_state.last_sig = ""
                jarvis_alert("Stop Loss hit, capital safe.", type="exit")

    # --- 📺 DISPLAY ---
    c1, c2, c3 = st.columns(3)
    c1.metric("LIVE PRICE", f"${ltp}")
    c2.metric("SIGNAL", st.session_state.last_sig if st.session_state.last_sig else "SCANNING")
    c3.metric("PNL POINTS", f"{round(abs(ltp - st.session_state.entry),2) if st.session_state.entry > 0 else 0}")

    st.markdown("---")
    col_chart, col_info = st.columns([2, 1])
    
    with col_chart:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange', width=2)))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_info:
        sig_col = "#00ff00" if "BUY" in st.session_state.last_sig else "#ff4b4b" if "SELL" in st.session_state.last_sig else "#555555"
        st.markdown(f"""
            <div style='background:#000; padding:20px; border-radius:15px; border:3px solid {sig_col}; text-align:center;'>
                <h1 style='color:{sig_col};'>{st.session_state.last_sig if st.session_state.last_sig else "WAITING"}</h1>
                <p style='color:white;'>Entry: ${st.session_state.entry if st.session_state.entry > 0 else '---'}</p>
                <p style='color:#00ff00;'>Target: +250 Pts</p>
                <hr>
                <button onclick="window.location.reload();">Manual Refresh</button>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Reset For Next Trade", use_container_width=True):
            st.session_state.last_sig = ""
            st.session_state.entry = 0.0
            st.session_state.target_hit = False
            st.rerun()
else:
    st.error("📡 Connecting...")
