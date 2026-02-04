import streamlit as st
from engine import get_market_data, get_news_impact # इंजन से कनेक्शन
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Jarvis Module A", layout="wide")
st_autorefresh(interval=2000, key="jarvis_sync")

st.title("🏛️ JARVIS: MODULE TESTING (NEWS)")

# डेटा लाना
df = get_market_data()

if not df.empty:
    # न्यूज़ पॉइंट टेस्ट करना
    atr_val, news_stat = get_news_impact(df)
    
    c1, c2 = st.columns(2)
    c1.metric("NIFTY LIVE", f"₹{df['Close'].iloc[-1]}")
    
    # न्यूज़ का डिस्प्ले
    color = "inverse" if news_stat == "HIGH" else "normal"
    c2.metric("NEWS FLOW (ATR)", f"{atr_val}", delta=news_stat, delta_color=color)
    
    if news_stat == "HIGH":
        st.warning("🚨 जार्विस न्यूज़ अलर्ट: बाज़ार में हलचल तेज़ है, बड़ा मूव आ सकता है!")
else:
    st.info("📡 जार्विस इंजन डेटा सिंक कर रहा है... कृपया रुकें।")
