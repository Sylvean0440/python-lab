# flask_kb.py —— 知识库助手（Flask 完整版）
import os, json, re
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'   # 国内镜像

import requests
from flask import Flask, request
from sentence_transformers import SentenceTransformer, util

# ===== 读 API key =====
cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]
url = 'https://api.deepseek.com/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

# ===== 读配置 + 加载模型 + 编码笔记 =====
config = json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'), encoding='utf-8'))
WIKI_DIR = os.path.join(config['vaultDir'], 'wiki')

model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
note_files = []
for fname in os.listdir(WIKI_DIR):
    if fname.endswith('.md'):
        content = open(os.path.join(WIKI_DIR, fname), encoding='utf-8').read()
        note_files.append((fname, content))
embeddings = model.encode([c for _, c in note_files])

# ===== 普通函数：搜索（不注册）=====
def search_notes(query):
    q_vec = model.encode(query)                        # 问题 → 向量
    scores = util.cos_sim(q_vec, embeddings)[0]        # 算相似度
    top_idx = scores.argsort(descending=True)[:3]      # 取最相似 3 篇
    return [note_files[i][1] for i in top_idx]         # 返回这 3 篇内容

# ===== 普通函数：调 API（不注册）=====
def ask_ai(question, context):
    messages = [
        {'role': 'system', 'content': '你是知识库助手，请根据下面提供的资料回答用户问题，不要说"根据资料"这种话。'},
        {'role': 'user', 'content': f'资料：\n{context}\n\n问题：{question}'},
    ]
    r = requests.post(url, headers=headers, json={'model': 'deepseek-chat', 'messages': messages})
    return r.json()['choices'][0]['message']['content']

# ===== 注册函数：循环的入口 =====
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':                       # 用户点了「提问」
        question = request.form['question']            # ① 拿到问题
        context = '\n\n'.join(search_notes(question))  # ② 搜笔记
        answer = ask_ai(question, context)             # ③ 调 AI
        return answer                                   # ④ 返回回答
    return '''                                         # GET：显示表单
        <form method="post">
            <input name="question" placeholder="问我任何问题" style="width:400px">
            <button type="submit">提问</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
