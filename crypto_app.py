import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 🎯 1. SUPREME SETTINGS ---
st.set_page_config(page_title="JARVIS REBORN v107", layout="wide")
st_autorefresh(interval=3000, key="jarvis_v107_final")

# --- 🔊 2. MASTER VOICE (Hindi Re-Stored) ---
def jarvis_speak(text):
    if text:
        js = f"<script>window.speechSynthesis.cancel(); var m = new SpeechSynthesisUtterance('{text}'); m.lang='hi-IN'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 🧠 3. PERMANENT BRAIN (No Movement) ---
if "init" not in st.session_state:
    st.session_state.update({
        "st_lock": False, "cr_lock": False, "st_sig": "SCANNING", "cr_sig": "SCANNING",
        "st_ep": 0.0, "st_sl": 0.0, "st_tg": 0.0, "balance": 120.0
    })

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🛡️ JARVIS REBORN v107.0</h1>", unsafe_allow_html=True)

if st.button("🔊 ACTIVATE JARVIS SYSTEM (आवाज़ यहाँ से शुरू करें)"):
    jarvis_speak("नमस्ते राजवीर सर, जार्विस का सबसे मज़बूत सिस्टम अब लाइव है।")

col_st, col_cr = st.columns(2)

# --- 📈 SECTION A: NSE (No-YFinance High-Speed Logic) ---
with col_st:
    st.header("📈 NSE (Fast Feed)")
    try:
        # Alternate Data Source for Nifty
        url_nse = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url_nse, headers=headers, timeout=5).json()
        
        price_data = res['chart']['result'][0]['indicators']['quote'][0]['close']
        time_data = res['chart']['result'][0]['timestamp']
        
        df_st = pd.DataFrame({'Close': price_data}, index=pd.to_datetime(time_data, unit='s'))
        df_st = df_st.dropna()
        
        if not df_st.empty:
            ltp = round(df_st['Close'].iloc[-1], 2)
            df_st['E9'] = ta.ema(df_st['Close'], length=9)
            df_st['E21'] = ta.ema(df_st['Close'], length=21)

            if not st.session_state.st_lock:
                if df_st['E9'].iloc[-1] > df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "CALL", "st_ep": ltp, "st_sl": ltp-45, "st_tg": ltp+250, "st_lock": True})
                    jarvis_speak("एन एस ई कॉल सिग्नल लॉक्ड")
                elif df_st['E9'].iloc[-1] < df_st['E21'].iloc[-1]:
                    st.session_state.update({"st_sig": "PUT", "st_ep": ltp, "st_sl": ltp+45, "st_tg": ltp-250, "st_lock": True})
                    jarvis_speak("एन एस ई पुट सिग्नल लॉक्ड")

            st.metric("NIFTY 50", f"₹{ltp}")
            st.success(f"📌 {st.session_state.st_sig} | Entry: {st.session_state.st_ep} | SL: {st.session_state.st_sl}")
            
            fig_st = go.Figure(data=[go.Scatter(x=df_st.index, y=df_st['Close'], line=dict(color='#00FF00', width=2))])
            fig_st.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_st, use_container_width=True)
    except: st.info("🔄 NSE डेटा लाइन बिजी है, री-कनेक्ट कर रहा हूँ...")

# --- ₿ SECTION B: CRYPTO (Multi-Server Unstoppable Feed) ---
with col_cr:
    st.header("₿ CRYPTO (BTC/USD)")
    ltp_cr = 0.0
    # 3-Way Fail-Safe Data
    sources = ["https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", 
               "https://api.coinbase.com/v2/prices/BTC-USD/spot"]
    
    for url in sources:
        try:
            r = requests.get(url, timeout=3).json()
            ltp_cr = float(r['price']) if 'price' in r else float(r['data']['amount'])
            if ltp_cr > 0: break
        except: continue

    if ltp_cr > 0:
        if not st.session_state.cr_lock:
            st.session_state.update({"cr_sig": "READY", "cr_ep": ltp_cr, "cr_sl": ltp_cr-200, "cr_tg": ltp_cr+600, "cr_lock": True})
            jarvis_speak("क्रिप्टो सिग्नल अपडेट हो गया है")

        st.metric("BTC PRICE", f"${round(ltp_cr, 2)}")
        qty = round((st.session_state.balance * 10) / ltp_cr, 4)
        st.warning(f"💰 Qty: {qty} BTC | Bal: $120")
        st.info(f"📌 {st.session_state.cr_sig} | E: {st.session_state.cr_ep}")
    else: st.info("🔄 क्रिप्टो डेटा इंतज़ार में है...")

st.write("---")
if st.button("🔄 RESET ALL (नया ट्रेड स्कैन करें)"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
