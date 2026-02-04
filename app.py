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
# app.py में न्यूज़ का अपडेट
import streamlit as st
from engine import get_market_data, apply_javed_strategy, get_news_impact # नया फंक्शन जोड़ा

st.title("🏛️ JARVIS COMMANDER v1.1")

df = get_market_data()
df = apply_javed_strategy(df)

# न्यूज़ का डेटा इंजन से खींचना
atr_value, news_status = get_news_impact(df)

# डैशबोर्ड पर दिखाना
c1, c2, c3 = st.columns(3)
c1.metric("LTP", f"₹{df['Close'].iloc[-1]}")
c2.metric("News Flow (ATR)", f"{atr_value}")

if news_status == "HIGH":
    c3.warning("🚨 ALERT: NEWS IMPACT DETECTED!")
else:
    c3.success("✅ MARKET: STABLE")
