import requests
import re

cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]
url = 'https://api.deepseek.com/chat/completions'
headers = {'Authorization': f'Bearer {key}',
           'Content-Type': 'application/json',}
data = {'model': 'deepseek-flash', 'messages': [{'role': 'user', 'content': '用一句话回复：你好'},],}
r = requests.post(url, headers=headers, json=data)
reply = r.json()['choices'][0]['message']['content']
print(reply)