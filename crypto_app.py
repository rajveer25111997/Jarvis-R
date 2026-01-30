import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time
import warnings
from datetime import datetime

# --- 🎯 1. CRYPTO CORE SETUP ---
warnings.filterwarnings('ignore')
st.set_page_config(page_title="CRYPTO JARVIS", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=1000, key="crypto_sync") # Ultra-fast for Crypto

# --- 🧠 2. DATA ENGINE (Global Assets) ---
def get_crypto_data(coin):
    try:
        # Crypto symbols: BTC-USD, ETH-USD, etc.
        df = yf.download(coin, period="1d", interval="1m", progress=False, auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df
    except: return None

# --- 🔍 3. STATIC UI ---
st.markdown("<h1 style='text-align:center; color:#f7931a; margin:0;'>₿ CRYPTO JARVIS OS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>24/7 GLOBAL MARKET SCANNER | MASTER EDITION</p>", unsafe_allow_html=True)

if "crypto_trades" not in st.session_state: st.session_state.crypto_trades = 0
if "last_sig" not in st.session_state: st.session_state.last_sig = ""
if "entry_usd" not in st.session_state: st.session_state.entry_usd = 0.0

# --- 🏗️ 4. NO-BLINK CRYPTO BRAIN ---
live_crypto = st.empty()

@st.fragment
def crypto_execution_engine():
    with st.sidebar:
        coin_choice = st.selectbox("Select Coin:", ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD"])
    
    df = get_crypto_data(coin_choice)
    
    if df is not None:
        price = round(float(df['Close'].iloc[-1]), 2)
        
        # 📈 Javed (9/21) & 200 EMA (The Whale Line)
        df['E9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['E21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['E200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # Whale Radar (Crypto Volume Shock)
        vol_spike = df['Volume'].iloc[-1] > (df['Volume'].rolling(20).mean().iloc[-1] * 2.0)
        
        # 🎯 Master Logic for Crypto
        is_buy = (df['E9'].iloc[-1] > df['E21'].iloc[-1]) and (price > df['E200'].iloc[-1])
        is_sell = (df['E9'].iloc[-1] < df['E21'].iloc[-1]) and (price < df['E200'].iloc[-1])
        
        if is_buy: sig, col = "🚀 CRYPTO BUY", "#00ff00"
        elif is_sell: sig, col = "📉 CRYPTO SELL", "#ff4b4b"
        else: sig, col = "⌛ SCANNING...", "#555555"

        # Voice Alerts (Global Edition)
        if "BUY" in sig or "SELL" in sig:
            if st.session_state.last_sig != sig:
                st.session_state.crypto_trades += 1
                st.session_state.entry_usd = price
                st.session_state.last_sig = sig
                voice = f"Rajveer Sir, Crypto Alert! {sig} on {coin_choice} at {price} dollars."
                st.components.v1.html(f"<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('{voice}'));</script>", height=0)

        # UI RENDERING
        with live_crypto.container():
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown(f"""
                    <div style="background:#111; padding:25px; border-radius:15px; border:1px solid #f7931a; text-align:center; height:450px; display:flex; flex-direction:column; justify-content:center;">
                        <h4 style="color:gray;">{coin_choice} PRICE</h4>
                        <h1 style="color:#f7931a; font-size:50px;">${price}</h1>
                        <hr style="border-color:#333;">
                        <h3 style="color:{col};">{sig}</h3>
                        <p style="color:white;">WHALE RADAR: {'⚡ ACTIVE' if vol_spike else 'WAITING'}</p>
                        <p style="color:gray;">TRADES: {st.session_state.crypto_trades}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Karishma SL for Crypto (Stricter SL - 1.5% for Crypto)
            st.markdown(f"""
                <div style="background:#07090f; padding:20px; border-radius:20px; border:3px solid {col}; text-align:center; margin-top:10px;">
                    <div style="display:flex; justify-content:space-around;">
                        <div><p style="color:gray;">ENTRY</p><h2 style="color:white;">${st.session_state.entry_usd if st.session_state.entry_usd>0 else '---'}</h2></div>
                        <div><p style="color:#00ff00;">TGT (+2%)</p><h2 style="color:#00ff00;">${round(st.session_state.entry_usd*1.02, 2) if st.session_state.entry_usd>0 else '---'}</h2></div>
                        <div><p style="color:#ff4b4b;">KARISHMA SL (-1%)</p><h2 style="color:#ff4b4b;">${round(st.session_state.entry_usd*0.99, 2) if st.session_state.entry_usd>0 else '---'}</h2></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# 🚀 Launch Crypto Jarvis
crypto_execution_engine()
