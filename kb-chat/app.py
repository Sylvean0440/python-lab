# app.py —— 知识库聊天机器人
import json
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'   # 国内镜像

import requests, re
import streamlit as st
from sentence_transformers import SentenceTransformer, util

# ===== 读 API key =====
cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]
url = 'https://api.deepseek.com/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

# ===== 加载模型（缓存）=====
@st.cache_resource
def load_model():
    return SentenceTransformer('BAAI/bge-small-zh-v1.5')

model = load_model()

# ===== 加载笔记（缓存）=====
config = json.load(open(os.path.join(os.path.dirname(__file__),'config.json'),encoding='utf-8'))
VAULT_DIR = config['vaultDir']
WIKI_DIR = os.path.join(VAULT_DIR,'wiki')


@st.cache_data
def load_notes():
    note_files = []
    for fname in os.listdir(WIKI_DIR):
        if fname.endswith('.md'):
            content = open(os.path.join(WIKI_DIR, fname), encoding='utf-8').read()
            note_files.append((fname, content))
    embeddings = model.encode([c for _, c in note_files])
    return note_files, embeddings

note_files, embeddings = load_notes()

# ===== 搜索函数（先定义，后面才用）=====
def search_notes(query):
    q_vec = model.encode(query)                        # 问题 → 向量
    scores = util.cos_sim(q_vec, embeddings)[0]        # 算相似度
    top_idx = scores.argsort(descending=True)[:3]      # 取最相似 3 篇
    return [note_files[i][1] for i in top_idx]         # 返回这 3 篇内容

# ===== 调 API 函数 =====
def ask_ai(question, context):
    messages = st.session_state['messages']
    messages.append({
    'role': 'user',
    'content': f'资料：\n{context}\n\n问题:{question}',
    'display_content': question
})
    api_messages = [
    {'role': message['role'], 'content': message['content']}
    for message in messages
]
    r = requests.post(url, headers=headers, json={'model': 'deepseek-chat', 'messages': api_messages})
    answer =  r.json()['choices'][0]['message']['content']
    messages.append({'role':'assistant','content':answer})
    return answer

# ===== 页面 =====
st.write(f'已加载 {len(note_files)} 篇笔记')
st.title('知识库助手')
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {
            'role': 'system',
            'content': '你是知识库助手，请根据下面提供的资料回答用户问题，不要说"根据资料"这种话。'
        }
    ]

if st.button('清空会话'):
    st.session_state['messages'] = st.session_state['messages'][:1]
    st.success('对话历史已清空')

with st.form('question_form'):
    question = st.text_input('问我任何关于你笔记的问题:')
    submitted = st.form_submit_button('发送')
if submitted and question.strip():
    context = '\n\n'.join(search_notes(question))
    answer = ask_ai(question, context)
for message in st.session_state['messages']:
    if message['role'] == 'system':
        continue
    with st.chat_message(message['role']):
        st.write(message.get('display_content', message['content']))

                            
                                                           
