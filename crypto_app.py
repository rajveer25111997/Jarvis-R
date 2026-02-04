
import streamlit as st
import pandas as pd
import requests

# राजवीर सर, यह कोड 30 सेकंड में लोड हो जाएगा
st.set_page_config(page_title="Jarvis Crypto Quick", layout="wide")
st.title("₿ JARVIS CRYPTO QUICK v161")

def get_btc():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        return requests.get(url).json()['price']
    except: return "Syncing..."

price = get_btc()
st.metric("BITCOIN (BTC/USDT)", f"${price}")

st.info("📡 जार्विस का भारी इंजन बैकग्राउंड में लोड हो रहा है, कृपया 1 मिनट और दें।")

if st.button("🔄 FORCE REFRESH"):
    st.rerun()
