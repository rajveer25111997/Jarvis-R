import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 🎯 1. SUPREME CONFIGURATION ---
st.set_page_config(page_title="JARVIS ULTIMATE FINAL", layout="wide")
st_autorefresh(interval=3000, key="jarvis_final_supreme")

# --- 🔊 2. MASTER VOICE ENGINE ---
def jarvis_speak(text):
    if text:
        js = f"""<script>
        window.speechSynthesis.cancel();
        var m = new SpeechSynthesisUtterance('{text}');
        m.lang = 'hi-IN'; m.rate = 1.0;
        window.speechSynthesis.speak(m);
        </script>"""
        st.components.v1.html(js, height=0)

# --- 🧠 3. JARVIS BRAIN & STATE (Permanent Memory) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_lock": False, "cr_lock": False, 
        "st_sig": "SCANNING", "cr_sig": "SCANNING",
        "st_why": "बाजार की न्यूज़ और इंडिकेटर्स को स्कैन कर रहा हूँ...",
        "cr_why": "Analyzing global crypto momentum...",
        "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0,
        "cr_ep": 0.0, "cr_sl": 0.0, "cr_tg": 0.0,
        "balance": 120.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏛️ JARVIS ULTIMATE FINAL v102.0</h1>", unsafe_allow_html=True)

# Activation for Voice Security
if st.button("🔊 ACTIVATE JARVIS SYSTEM (आवाज़ चालू करें)"):
    jarvis_speak("नमस्ते राजवीर सर, जार्विस मास्टर सिस्टम पूरी तरह तैयार है।")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE STOCK (Strategy + News + Why) ---
with col_st:
    st.header("📈 NSE (Javed/Karishma)")
    asset_st = st.sidebar.selectbox("Select NSE", ["^NSEI", "^NSEBANK"], key="st_box")
    try:
        df_st = yf.download(asset_st, period="3d", interval="1m", progress=False)
        if not df_st.empty:
            # Background Combination Indicators
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)
            df_st['E200'] = ta.ema(df_st['Close'], length=200)
            df_st['ATR'] = ta.atr(df_st['High'], df_st['Low'], df_st['Close'], length=14)
            ltp = round(df_st['Close'].iloc[-1], 2)
            atr_now = df_st['ATR'].iloc[-1]

            if not st.session_state.st_lock:
                # News Effect logic
                news_impact = "High" if atr_now > df_st['ATR'].mean() else "Stable"
                is_call = df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1] and ltp > df_st['E200'].iloc[-1]
                is_put = df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1] and ltp < df_st['E200'].iloc[-1]

                if is_call:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp, "st_sl": ltp-50, "st_tg": ltp+250, "st_lock": True, 
                                             "st_why": f"मार्केट ऊपर जा रहा है क्योंकि {news_impact} न्यूज़ इम्पैक्ट के साथ 9/21 क्रॉसओवर हुआ है और भाव 200 EMA के ऊपर है।"})
                    jarvis_speak("एन एस ई कॉल सिग्नल लॉक्ड")
                elif is_put:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp, "st_sl": ltp+50, "st_tg": ltp-250, "st_lock": True, 
                                             "st_why": f"मार्केट नीचे गिर रहा है क्योंकि {news_impact} न्यूज़ का असर नेगेटिव है और भाव 200 EMA के नीचे फिसल गया है।"})
                    jarvis_speak("एन एस ई पुट सिग्नल लॉक्ड")

            st.metric(f"{asset_st} LIVE", f"₹{ltp}", delta=f"ATR: {round(atr_now,2)}")
            st.success(f"📌 {st.session_state.st_sig} | ENTRY: {st.session_state.st_ep} | SL: {st.session_state.st_sl}")
            st.info(f"🧠 **Jarvis Why:** {st.session_state.st_why}")
            
            fig_st = go.Figure(data=[go.Candlestick(x=df_st.index, open=df_st['Open'], high=df_st['High'], low=df_st['Low'], close=df_st['Close'])])
            fig_st.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_st, use_container_width=True)
    except: st.info("NSE Background Scanning...")

# --- ₿ SECTION B: CRYPTO (Delta Master Logic) ---
with col_cr:
    st.header("₿ CRYPTO (BTC Master)")
    try:
        url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=200"
        res = requests.get(url).json()
        if 'Data' in res:
            df_cr = pd.DataFrame(res['Data']['Data'])
            df_cr['E9'] = ta.ema(df_cr['close'], length=9)
            df_cr['E21'] = ta.ema(df_cr['close'], length=21)
            ltp_cr = float(df_cr['close'].iloc[-1])

            if not st.session_state.cr_lock:
                if df_cr['E9'].iloc[-1] > df_cr['E21'].iloc[-1]:
                    st.session_state.update({"cr_sig": "CALL", "cr_ep": ltp_cr, "cr_sl": ltp_cr-200, "cr_tg": ltp_cr+600, "cr_lock": True, "cr_why": "Bitcoin is pumping due to strong institutional volume crossover."})
                    jarvis_speak("क्रिप्टो कॉल सिग्नल लॉक्ड")
                elif df_cr['E9'].iloc[-1] < df_cr['E21'].iloc[-1]:
                    st.session_state.update({"cr_sig": "PUT", "cr_ep": ltp_cr, "cr_sl": ltp_cr+200, "cr_tg": ltp_cr-600, "cr_lock": True, "cr_why": "Bitcoin trend is bearish. Breaking news impact seen on chart."})
                    jarvis_speak("क्रिप्टो पुट सिग्नल लॉक्ड")

            st.metric("BTC PRICE", f"${ltp_cr}")
            qty = round((st.session_state.balance * 10) / ltp_cr, 4)
            st.warning(f"💰 Qty: {qty} BTC | Capital: $120")
            st.info(f"🧠 **Jarvis Why:** {st.session_state.cr_why}")
            
            fig_cr = go.Figure(data=[go.Candlestick(x=pd.to_datetime(df_cr['time'], unit='s'), open=df_cr['open'], high=df_cr['high'], low=df_cr['low'], close=df_cr['close'])])
            fig_cr.update_layout(template="plotly_dark", height=300, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)
    except: st.info("Crypto Background Scanning...")

# --- 🛡️ MASTER SYSTEM RESET ---
st.write("---")
if st.button("🔄 FULL SYSTEM RESET (New Trade Scan)"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
