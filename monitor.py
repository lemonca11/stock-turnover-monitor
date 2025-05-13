import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

API_KEY = 'YWXKQH5RRGUN5YCL'
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
BASE_URL = 'https://api.twelvedata.com/time_series'

def get_intraday_turnover(symbol, date):
    start = f"{date} 09:30:00"
    end = f"{date} 12:00:00"
    params = {
        'symbol': symbol,
        'interval': '1min',
        'start_date': start,
        'end_date': end,
        'apikey': API_KEY,
        'format': 'JSON',
        'outputsize': 180
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if 'values' not in data or not data['values']:
        print(f"{symbol} ❌ 无数据：{data.get('message', '返回为空')}")
        return None
    df = pd.DataFrame(data['values'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['volume'] = df['volume'].astype(float)
    df['close'] = df['close'].astype(float)
    df['成交额'] = df['volume'] * df['close']
    return df['成交额'].sum()

def main():
    now = datetime.now()
    today = (now - timedelta(days=0)).date()
    yesterday = (now - timedelta(days=1)).date()

    results = []

    for symbol in SYMBOLS:
        print(f"🔍 正在分析 {symbol}...")
        today_val = get_intraday_turnover(symbol, str(today))
        time.sleep(1.5)
        yesterday_val = get_intraday_turnover(symbol, str(yesterday))
        time.sleep(1.5)

        if today_val is None or yesterday_val is None:
            continue

        if today_val < yesterday_val:
            diff = yesterday_val - today_val
            results.append({
                '股票代码': symbol,
                '今日成交额（百万美元）': round(today_val / 1e6, 2),
                '昨日成交额（百万美元）': round(yesterday_val / 1e6, 2),
                '差额（百万美元）': round(diff / 1e6, 2)
            })

    os.makedirs('static', exist_ok=True)
    filename = f"static/成交额预警_{today}.csv"

    if results:
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)
        print("✅ 已保存成交额异常数据为：", filename)
    else:
        df = pd.DataFrame(columns=['股票代码', '今日成交额（百万美元）', '昨日成交额（百万美元）', '差额（百万美元）'])
        df.to_csv(filename, index=False)
        print("✅ 所有股票今日成交额 ≥ 昨日，无预警。")

if __name__ == "__main__":
    main()
