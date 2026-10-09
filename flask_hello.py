# flask_hello.py —— 第一个 Flask 网页
from flask import Flask

app = Flask(__name__)                  # ① 创建 Flask 应用（服务器）

@app.route('/')                        # ② 路由：访问根路径 "/" 时，调用下面的函数
def home():
    return '<h1>你好，Flask！</h1>'      # ③ 返回 HTML（浏览器会显示它）

if __name__ == '__main__':
    app.run(debug=True)                # ④ 启动服务器（默认 http://localhost:5000）
