from flask import Flask, render_template
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    today = datetime.now().date()
    file_path = f"static/成交额预警_{today}.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if df.empty:
            return render_template('index.html', message="✅ 今日暂无成交额预警，全部股票成交良好。", table_html=None)
        else:
            table_html = df.to_html(index=False, classes='table table-striped table-bordered')
            return render_template('index.html', message="⚠️ 今日中午成交额低于昨日的股票：", table_html=table_html)
    else:
        return render_template('index.html', message="⚠️ 今日数据尚未生成，请稍后刷新。", table_html=None)

if __name__ == '__main__':
    app.run()
