import streamlit as st
import requests
import time

# राजवीर सर, यह कोड कभी नहीं अटकेगा
st.set_page_config(page_title="Jarvis Crypto Final", layout="wide")
st.title("₿ JARVIS CRYPTO FINAL v162")

def get_btc_price():
    # बैकअप 1: बाइनेंस
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2)
        return r.json()['price']
    except:
        # बैकअप 2: कॉइनबेस (अगर बाइनेंस फेल हो जाए)
        try:
            r = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", timeout=2)
            return r.json()['data']['amount']
        except:
            return "Server Offline"

price = get_btc_price()

# बड़ा और साफ़ डिस्प्ले
st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:30px; border-radius:15px; border:2px solid #F7931A; text-align:center;">
        <h2 style="color:#F7931A; margin:0;">BITCOIN LIVE PRICE</h2>
        <h1 style="color:white; font-size:60px; margin:10px;">${price}</h1>
    </div>
""", unsafe_allow_html=True)

st.warning("⚠️ राजवीर सर, अगर $Syncing दिख रहा है, तो एक बार 'RESET' बटन दबाएं।")

if st.button("🔄 FORCE SYNC DATA"):
    st.rerun()
