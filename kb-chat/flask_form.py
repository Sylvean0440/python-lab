# flask_form.py —— 让网页接收用户输入
from flask import Flask, request          # 多引入一个 request（用来读请求）

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])  # 允许 GET（看页面）和 POST（提交）
def home():
    if request.method == 'POST':          # 用户点了「提交」（POST 请求）
        name =  request.form['name']       # 取出输入框里 name 的值
        return f'<h1>你好，{name}！</h1>'  # 返回问候
    return '''                             # 否则（GET 请求）显示表单
        <form method="post">
            <input name="name" placeholder="输入你的名字">
            <button type="submit">提交</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
