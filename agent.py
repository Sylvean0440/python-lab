import requests
import re
import json
import os
cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml',encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)',cred)[0]
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
tools=[{
    'type': 'function',
    'function': {
        'name': 'search_notes',
        'description': '搜索知识库笔记，返回相关笔记内容',
        'parameters':{
            'type': 'object',
            'properties':{'keyword': {'type': 'string', 'description': '要搜索的关键词'}},
            'required': ['keyword']
            }
        }
    }
]
question = input('你想问什么？')
messages = [
    {'role': 'system', 'content': '你是知识库助手。回答前先调用search_notes 搜索相关资料。'},
    {'role': 'user', 'content': question},
]
r = requests.post(url, headers=headers,json={'model':'deepseek-flash',
                                             'messages':messages, 'tools':tools}
)
msg = r.json()['choices'][0]['message']
if msg.get('tool_calls'):
    messages.append({'role': 'assistant', 'content': msg.get('content') or '','tool_calls':msg['tool_calls']}
)
    for tc in msg['tool_calls']:
        args = json.loads(tc['function']['arguments'])
        result = search_notes(args['keyword'])
        messages.append({'role':'tool', 'tool_call_id':tc['id'],'content':result})
    r2 = requests.post        (url, headers=headers, json={'model': 'deepseek-flash', 'messages': messages})
    print(r2.json()['choices'][0]['message']['content']) 
else:
    print(msg['content'])                             
                                    
                                             
