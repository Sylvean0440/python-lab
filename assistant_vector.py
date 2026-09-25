import requests
import re
import json
import os
from config import VAULT_DIR
from sentence_transformers import SentenceTransformer, util

cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]
url = 'https://api.deepseek.com/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

SYSTEM_PROMPT = '你是知识库助手。回答用户问题前，先调用 search_notes 搜索相关资料，再基于资料回答。'
MAX_ROUNDS = 8

# ===== 向量检索准备（只做一次）=====
print('正在加载模型 + 编码笔记，请稍候...')
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

notes_dir = os.path.join(VAULT_DIR, 'wiki')
note_files = []                          # 存 (文件名, 内容)
for fname in os.listdir(notes_dir):
    if not fname.endswith('.md'):
        continue
    content = open(notes_dir + '/' + fname, encoding='utf-8').read()
    note_files.append((fname, content))

contents = [c for _, c in note_files]
embeddings = model.encode(contents)      # 所有笔记 → 向量（一次性）
print(f'准备完成！共编码 {len(note_files)} 篇笔记')


def search_notes(keyword):
    q_vec = model.encode(keyword)                    # 关键词 → 向量
    scores = util.cos_sim(q_vec, embeddings)[0]      # 和每篇笔记的相似度
    top_idx = scores.argsort(descending=True)[:2]    # 最相似的 2 篇的索引
    return '\n\n'.join(note_files[i][1] for i in top_idx)


tools = [{
    'type': 'function',
    'function': {
        'name': 'search_notes',
        'description': '搜索知识库笔记，返回相关笔记内容',
        'parameters': {
            'type': 'object',
            'properties': {'keyword': {'type': 'string', 'description': '要搜索的关键词'}},
            'required': ['keyword']
        }
    }
}]

print('=== 知识库问答助手（向量检索版，输入 q 退出）===')

while True:
    question = input('\n你想问什么？')
    if question.strip().lower() == 'q':
        print('再见！')
        break
    if not question.strip():
        continue

    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': question},
    ]

    for round_num in range(1, MAX_ROUNDS + 1):
        r = requests.post(url, headers=headers,
                          json={'model': 'deepseek-flash', 'messages': messages, 'tools': tools})
        msg = r.json()['choices'][0]['message']

        if not msg.get('tool_calls'):
            print('\n' + msg['content'])
            break

        messages.append({'role': 'assistant', 'content': msg.get('content') or '',
                         'tool_calls': msg['tool_calls']})
        for tc in msg['tool_calls']:
            args = json.loads(tc['function']['arguments'])
            print(f'  [搜索] {args["keyword"]}')
            result = search_notes(args['keyword'])
            messages.append({'role': 'tool', 'tool_call_id': tc['id'], 'content': result})
    else:
        print('\n（达到最大轮数，已停止）')
