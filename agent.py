import requests
import re
import json
import os

cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]
url = 'https://api.deepseek.com/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}


def search_notes(keyword):
    notes_dir = 'D:/obsidian/poosa/个人ai知识库/wiki'
    hits = []
    for fname in os.listdir(notes_dir):
        if not fname.endswith('.md'):
            continue
        content = open(notes_dir + '/' + fname, encoding='utf-8').read()
        if keyword in content:
            hits.append(content)
    return '\n\n'.join(hits[:2])


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

question = input('你想问什么？')
messages = [
    {'role': 'system', 'content': '你是知识库助手。回答前先调用 search_notes 搜索相关资料。'},
    {'role': 'user', 'content': question},
]

# ===== Agent 循环：反复"调 AI → 执行工具"，直到 AI 不再调工具 =====
max_rounds = 8          # 最多 8 轮，防止无限循环

for round_num in range(1, max_rounds + 1):
    # 每次调用都带上 tools（这样 AI 随时能通过正规渠道调工具）
    r = requests.post(url, headers=headers,
                      json={'model': 'deepseek-flash', 'messages': messages, 'tools': tools})
    msg = r.json()['choices'][0]['message']

    # AI 不再调工具 → 它给出了最终回答，结束循环
    if not msg.get('tool_calls'):
        print(f'\n=== 第 {round_num} 轮：AI 给出最终回答 ===')
        print(msg['content'])
        break

    # AI 要调工具 → 把它的请求加进对话
    print(f'\n=== 第 {round_num} 轮：AI 要调 {len(msg["tool_calls"])} 个工具 ===')
    messages.append({'role': 'assistant', 'content': msg.get('content') or '',
                     'tool_calls': msg['tool_calls']})

    # 逐个执行工具，结果加进对话
    for tc in msg['tool_calls']:
        args = json.loads(tc['function']['arguments'])
        result = search_notes(args['keyword'])
        print(f'  -> search_notes("{args["keyword"]}")  搜到 {len(result)} 字')
        messages.append({'role': 'tool', 'tool_call_id': tc['id'], 'content': result})
else:
    print('\n（达到最大轮数，AI 还在调工具，已停止）')
