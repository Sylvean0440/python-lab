import requests
import re
note = open('D:/obsidian/poosa/个人ai知识库/wiki/技能清单.md',encoding='utf-8').read()
cred = open(r'C:\Users\Sylvean\.dsh\.credentials.yaml', encoding='utf-8').read()
key = re.findall(r'DEEPSEEK_API_KEY:\s*(sk-\S+)',cred)[0]
question = input('你想问什么?')
api_headers ={'Authorization':f'Bearer {key}','Content-Type':'application/json'}
data = {'model' : 'deepseek-flash', 'messages':[{'role':'system','content' :'你是知识库助手，只依据下面提供的资料回答，资料里没有的就说不知道，不要编造'},
                                                {'role':'user','content':f'资料:\n{note}\n\n问题:\n{question}'},],}
r = requests.post('https://api.deepseek.com/chat/completions',headers = api_headers , json=data)
print(r.json()['choices'][0]['message']['content'])
