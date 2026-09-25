import requests
import re
import os
from config import VAULT_DIR
notes_dir = os.path.join(VAULT_DIR, 'wiki')
files = os.listdir(notes_dir)
keywords = input('输入关键词（用空格分隔):').split()
hits = []
for fname in files:
    if not fname.endswith('.md'):
        continue
    content = open(notes_dir + '/' + fname, encoding='utf-8').read()
    score = 0
    for kw in keywords:
        if kw in content:
            score += 1
    if score > 0:
        hits.append((score,fname,content))
hits.sort(reverse=True)
top = hits[:2]
if not top:
    print('没有找到相关笔记')
    exit()
context = '\n\n'.join(c[2] for c in top)
cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)',cred)[0]
api_headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
data = {'model': 'deepseek-flash', 'messages':[{'role':'system','content':'你是知识库助手，只依据下面提供的资料回答，资料里没有的就说不知道,'},
                                               {'role':'user','content':f'资料：\n{context}\n\n问题：{' '.join(keywords)}'},
]}
r = requests.post('https://api.deepseek.com/chat/completions', headers=api_headers, json=data)
print(r.json()['choices'][0]['message']['content'])
