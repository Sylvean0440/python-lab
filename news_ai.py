import requests
import re

ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
resp = requests.get('https://www.qbitai.com/feed', headers=ua)
titles = re.findall(r'<title>(.*?)</title>', resp.text)[1:]

cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]

titles_text = '\n'.join(titles)

api_headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
data = {'model': 'deepseek-flash', 'messages': [
    {'role': 'system', 'content': '你是AI新闻助手，用中文简洁总结这些新闻标题，挑重点'},
    {'role': 'user', 'content': '今天的新闻标题:\n' + titles_text},
],}

r = requests.post('https://api.deepseek.com/chat/completions', headers=api_headers, json=data)
reply = r.json()['choices'][0]['message']['content']
print(reply)

out = open('D:/obsidian/poosa/个人ai知识库/wiki/今日AI要闻.md', 'w', encoding='utf-8')
out.write(reply)
out.close()
print('已保存到 Obsidian')
