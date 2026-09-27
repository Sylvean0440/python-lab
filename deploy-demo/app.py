# app.py —— 部署演示版（最简 Flask 网页，能上免费平台）
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        return f'<h1>你好，{name}！这是部署在云端的网页 🎉</h1>'
    return '''
        <h1>我的第一个云端网页</h1>
        <p>这个网页跑在云端服务器上，任何人打开这个网址都能访问！</p>
        <form method="post">
            <input name="name" placeholder="输入你的名字" style="width:300px">
            <button type="submit">提交</button>
        </form>
    '''

if __name__ == '__main__':
    app.run()
