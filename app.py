from flask import Flask, render_template
from monitor import run_monitor
import os

app = Flask(__name__)

@app.route('/')
def home():
    try:
        df = run_monitor()
        if df is not None and not df.empty:
            table_html = df.to_html(classes='table table-striped', index=False)
            return render_template('index.html', message=None, table_html=table_html)
        else:
            return render_template('index.html', message="⚠️ 今日数据尚未生成，请稍后刷新。", table_html=None)
    except Exception as e:
        return render_template('index.html', message=f"❌ 发生错误：{str(e)}", table_html=None)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
