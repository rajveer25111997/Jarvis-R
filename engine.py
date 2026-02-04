# engine.py - यहाँ हम एक-एक पॉइंट टेस्ट करेंगे
import pandas as pd
import pandas_ta as ta
import requests

def get_market_data():
    # पॉइंट: डेटा बैकअप (Point 1)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
    p = res['chart']['result'][0]['indicators']['quote'][0]['close']
    return pd.DataFrame({'Close': p}).dropna()

def apply_javed_strategy(df):
    # पॉइंट: जावेद 9/21 (Point 2)
    df['E9'] = ta.ema(df['Close'], length=9)
    df['E21'] = ta.ema(df['Close'], length=21)
    return df

# टेस्ट रन
data = get_market_data()
final_data = apply_javed_strategy(data)
print("जावेद पॉइंट टेस्ट सफल:", final_data.tail(1))
# --- न्यूज़ पॉइंट (ATR Logic) ---
def get_news_impact(df):
    """
    यह फंक्शन ATR के ज़रिए न्यूज़ का प्रभाव नापता है।
    High ATR = न्यूज़ का असर है, बड़ा मूव आएगा।
    """
    # ATR Calculate करना (14 कैंडल्स का औसत)
    df['ATR'] = ta.atr(df['Close'], df['Close'], df['Close'], length=14)
    
    current_atr = df['ATR'].iloc[-1]
    avg_atr = df['ATR'].tail(20).mean()
    
    # अगर अभी का ATR औसत से 20% ज़्यादा है, तो न्यूज़ का असर है
    news_effect = "HIGH" if current_atr > (avg_atr * 1.2) else "NORMAL"
    
    return round(current_atr, 2), news_effect
