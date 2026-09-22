import requests
import re
url = 'https://www.qbitai.com/feed'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
r = requests.get(url, headers=headers)
titles=re.findall(r'<title>(.*?)</title>',r.text)[1:]
links=re.findall(r'<link>(.*?)</link>',r.text)[1:]
for i in range(len(titles)):
    print(titles[i])
    print('  ' + links[i])
    print()