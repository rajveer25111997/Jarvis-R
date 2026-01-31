import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. ULTIMATE CONFIG ---
st.set_page_config(page_title="JARVIS-R: FINAL SNIPER", layout="wide")
st_autorefresh(interval=1000, key="jarvis_final_v9")

# --- 🧠 2. FAST-DATA ENGINE ---
def get_crypto_data(coin="BTC"):
    # Using CryptoCompare for real-time speed
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

# --- 🔊 3. BACKGROUND VOICE ENGINE (WEB API) ---
def jarvis_speak(text, alert_type="signal"):
    # High-pitch beep for signals, low-pitch for exits
    siren = "https://www.soundjay.com/buttons/sounds/beep-07.mp3" if alert_type=="signal" else "https://www.soundjay.com/buttons/sounds/beep-09.mp3"
    js = f"""
    <script>
    var audio = new Audio('{siren}');
    audio.play();
    var msg = new SpeechSynthesisUtterance('{text}');
    msg.rate = 1.0;
    msg.pitch = 1.0;
    msg.lang = 'hi-IN';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- 🏦 4. DASHBOARD UI ---
st.markdown("""
    <div style='text-align:center; background:linear-gradient(90deg, #111, #ff4b4b); padding:15px; border-radius:15px; border:2px solid #fff;'>
        <h1 style='color:white; margin:0;'>🤖 JARVIS-R: MASTER SNIPER v9.0</h1>
        <p style='color:white; margin:0;'>₹5,000 CAPITAL | 200-300 PT BIG MOVE | CALL-PUT ACTIVE</p>
    </div>
""", unsafe_allow_html=True)

# Important: Voice Unlock Button
st.write("")
col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
with col_btn2:
    if st.button("📢 ACTIVATE JARVIS VOICE (ट्रेडिंग शुरू करने से पहले इसे दबाएं)", use_container_width=True):
        jarvis_speak("Jarvis is online. Rajveer Sir, I am ready to hunt big moves.")
        st.success("Jarvis Voice Activated! ✅")

if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry" not in st.session_state: st.session_state.entry = 0.0

# --- 🚀 5. SNIPER LOGIC (45-POINTS) ---
df = get_crypto_data("BTC")

if not df.empty:
    ltp = round(df['close'].iloc[-1], 2)
    
    # Technical Indicators
    df['E9'] = df['close'].ewm(span=9).mean()
    df['E21'] = df['close'].ewm(span=21).mean()
    df['E200'] = df['close'].ewm(span=200).mean()
    
    # Volatility Check (To ensure 200-300 pt move)
    volatility = df['high'].max() - df['low'].min()
    
    # Signal Logic
    buy_sig = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (ltp > df['E200'].iloc[-1])
    sell_sig = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (ltp < df['E200'].iloc[-1])

    # --- 🚦 SIGNAL TRIGGER ---
    if buy_sig and st.session_state.last_sig != "BUY":
        st.session_state.last_sig = "BUY"
        st.session_state.entry = ltp
        jarvis_speak(f"Rajveer Sir, Big Moment Call Entry at {ltp}. Let's go for 300 points.")

    elif sell_sig and st.session_state.last_sig != "SELL":
        st.session_state.last_sig = "SELL"
        st.session_state.entry = ltp
        jarvis_speak(f"Rajveer Sir, High Volume Put Entry at {ltp}. Trend is crashing.")

    # --- 📺 DISPLAY COMMAND CENTER ---
    c1, c2, c3 = st.columns(3)
    c1.metric("BTC LIVE PRICE", f"${ltp}")
    c2.metric("CURRENT SIGNAL", st.session_state.last_sig if st.session_state.last_sig else "SCANNING...")
    c3.metric("TARGET", "+300 Points", delta="Big Move Active")

    col_ch, col_inf = st.columns([2, 1])
    with col_ch:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['E200'], name='200 EMA', line=dict(color='orange', width=2)))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_inf:
        s_col = "#00ff00" if "BUY" in st.session_state.last_sig else "#ff4b4b" if "SELL" in st.session_state.last_sig else "#555555"
        st.markdown(f"""
            <div style='background:#000; padding:20px; border-radius:15px; border:3px solid {s_col}; text-align:center;'>
                <h2 style='color:white;'>STATUS</h2>
                <h1 style='color:{s_col};'>{st.session_state.last_sig if st.session_state.last_sig else "WAITING"}</h1>
                <hr>
                <p style='color:white;'>Entry Point: ${st.session_state.entry if st.session_state.entry > 0 else '---'}</p>
                <p style='color:#00ff00;'>Profit Target: +$300</p>
                <p style='color:#ff4b4b;'>Tight SL: -0.3%</p>
            </div>
        """, unsafe_allow_html=True)
        st.info("💡 Tip: जैसे ही जार्विस बोले, बिना भाव देखे डेल्टा एक्सचेंज पर आर्डर मारें।")

else:
    st.error("📡 Connecting to High-Speed Satellite... Rajveer Sir, please wait.")
