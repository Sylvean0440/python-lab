# app.py —— 大学生小红书文案助手（垂直版）
import os, re
import requests
from flask import Flask, request

# ===== 读 API key（跟之前一样）=====
cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]
url = 'https://api.deepseek.com/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

# ===== 核心：大学生副业小红书文案的 prompt =====
PROMPT = """你是一个深谙大学生副业/赚钱痛点的小红书博主。请根据用户给的主题，生成一篇给大学生看的小红书笔记。

【标题】生成 3 个标题，每个不超过 20 字，用这些公式：
- 提问式（"大学生靠这个副业月入过千？"）
- 共鸣式（点出大学生缺钱的痛点）
- 数据型（"3个方法""第5条最赚钱"）
- 清单式（"学生党副业清单"）

【正文】400-600 字，要求：
- 口语化，像跟同学聊天，禁用"首先/其次/总之/综上所述"
- 用"姐妹们/同学们"或直接切入，别每次一样
- 至少 1 个真实细节（时薪、成本、踩坑经历）
- 至少 1 个情绪转折或吐槽（比如"一开始以为很简单，结果..."）
- 结尾引导评论互动（"你们还有什么方法？评论区说说"）

【标签】5-8 个，大学生副业相关（#大学生副业 #赚钱 #学生党 #副业 #AI工具 等），别堆砌无关标签。

主题："""

# ===== 调 AI 生成 =====
def generate(topic):
    messages = [
        {'role': 'system', 'content': PROMPT},
        {'role': 'user', 'content': topic},
    ]
    r = requests.post(url, headers=headers, json={'model': 'deepseek-chat', 'messages': messages})
    return r.json()['choices'][0]['message']['content']

# ===== Flask 网页 =====
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        topic = request.form['topic']          # 拿到用户输入的主题
        result = generate(topic)               # 调 AI 生成文案
        return f'<pre>{result}</pre>'          # <pre> 保留换行显示
    return '''
        <h1>大学生小红书文案助手</h1>
        <form method="post">
            <input name="topic" placeholder="输入主题，如：大学生靠AI工具赚钱" style="width:400px">
            <button type="submit">生成</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
