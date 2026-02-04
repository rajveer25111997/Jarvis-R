# app.py - यह ऑटोमैटिक अपडेट होगा
import streamlit as st
from engine import get_market_data, apply_javed_strategy # इंजन से इंपोर्ट
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=1000, key="jarvis_live")

st.title("🏛️ JARVIS FINAL DASHBOARD")

# इंजन को कॉल करना
df = get_market_data()
df = apply_javed_strategy(df)

ltp = df['Close'].iloc[-1]
st.metric("NIFTY LIVE", f"₹{ltp}")

if df['E9'].iloc[-1] > df['E21'].iloc[-1]:
    st.success("✅ JAVED SAYS: BUY CALL")
else:
    st.error("❌ JAVED SAYS: BUY PUT")
