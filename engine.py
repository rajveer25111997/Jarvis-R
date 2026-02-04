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
