import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

API_KEY = 'YWXKQH5RRGUN5YCL'
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
BASE_URL = 'https://api.twelvedata.com/time_series'

def get_intraday_turnover(symbol, date_str):
    start = f"{date_str} 09:30:00"
    end = f"{date_str} 12:00:00"
    params = {
        'symbol': symbol,
        'interval': '1min',
        'start_date': start,
        'end_date': end,
        'apikey': API_KEY,
        'format': 'JSON',
        'outputsize': 180
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
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
    except Exception as e:
        print(f"{symbol} ⚠️ 请求失败：{str(e)}")
        return None

def run_monitor():
    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    results = []
    for symbol in SYMBOLS:
        print(f"📊 检查 {symbol}...")
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

    return df  # 可供 Flask 页面读取显示

# 脚本独立运行支持
if __name__ == "__main__":
    run_monitor()
