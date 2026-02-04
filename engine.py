import pandas as pd
import pandas_ta as ta
import requests

# पॉइंट: डेटा फेचर (Source 1)
def get_market_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^NSEI?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        p = res['chart']['result'][0]['indicators']['quote'][0]['close']
        return pd.DataFrame({'Close': p}).dropna()
    except:
        return pd.DataFrame()

# पॉइंट: न्यूज़ इम्पैक्ट (ATR Logic)
def get_news_impact(df):
    if df.empty or len(df) < 14:
        return 0.0, "WAITING"
    
    # ATR नापना (बाज़ार की न्यूज़ वाली हलचल)
    df['ATR'] = ta.atr(df['Close'], df['Close'], df['Close'], length=14)
    current_atr = round(df['ATR'].iloc[-1], 2)
    
    # अगर हलचल (ATR) 5 से ज़्यादा है, तो न्यूज़ का असर है
    status = "HIGH" if current_atr > 5.0 else "NORMAL"
    return current_atr, status
