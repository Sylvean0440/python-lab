import requests
import re
import json
import os

cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]
url = 'https://api.deepseek.com/chat/completions'
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

SYSTEM_PROMPT = '你是知识库助手。回答用户问题前，先调用 search_notes 搜索相关资料，再基于资料回答。'
MAX_ROUNDS = 8


def search_notes(keyword):
    notes_dir = 'D:/obsidian/poosa/个人ai知识库/wiki'
    hits = []
    for fname in os.listdir(notes_dir):
        if not fname.endswith('.md'):
            continue
        content = open(notes_dir + '/' + fname, encoding='utf-8').read()
        score = content.count(keyword)      # 关键词出现次数
        if keyword in fname:
            score += 10                     # 文件名含关键词，重点加分
        if score > 0:
            hits.append((score, content))
    hits.sort(reverse=True)
    return '\n\n'.join(c for _, c in hits[:2])


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

print('=== 知识库问答助手（输入 q 退出）===')

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

    # Agent 循环：反复"调 AI → 执行工具"，直到 AI 给出最终回答
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
