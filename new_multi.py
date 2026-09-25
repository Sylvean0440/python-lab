import requests
import re
import os
from config import VAULT_DIR
from datetime import date
ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
sources = [
    'https://www.qbitai.com/feed',
    'https://www.infoq.cn/feed',
    'https://www.leiphone.com/feed',
    'https://www.zhidx.com/rss',
]

all_titles = []
for src in sources:
    try:
        resp = requests.get(src,headers=ua, timeout=15)
        titles = re.findall(r'<title>(.*?)</title>', resp.text)[1:]
        all_titles = all_titles + titles
        print(f'✓ 抓到 {len(titles)} 条')
    except Exception as e:
        print(f'失败：{e}')

titles_text = '\n'.join(all_titles)
cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)', cred)[0]

api_headers = {'Authorization': f'Bearer {key}' , 'Content-Type': 'application/json'}
data = {'model': 'deepseek-flash', 'messages': [{'role':'system','content':'你是AI新闻助手，用中文简洁总结这些新闻标题，挑重点，分主题' },{'role':'user','content':'今天的新闻标题:\n'+ titles_text},],}

r=requests.post('https://api.deepseek.com/chat/completions',headers = api_headers ,json=data)
reply = r.json()['choices'][0]['message']['content']
print(reply)
today = date.today()
filename = os.path.join(VAULT_DIR, 'wiki', f'今日AI要闻-{today}.md')
out = open(filename,'w',encoding='utf-8')
out.write(reply)
out.close()
print('已保存Obsidian')