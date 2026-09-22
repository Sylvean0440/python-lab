path = input('要分析哪个文件？')
try:
    f = open(path, encoding="utf-8")
except FileNotFoundError:
    print('文件打不开，请检查路径对不对')
    exit()
lines = f.readlines()
print('行数为', len(lines))
words = ''.join(lines)
print('字数为', len(words))
for line in lines:
    if line.startswith('#'):
        print(line)
result = f'行数为{len(lines)}\n字数为{len(words)}\n'
out = open('分析结果.txt', 'w', encoding='utf-8')
out.write(result)
out.close()
print('结果已保存到 分析结果.txt')
