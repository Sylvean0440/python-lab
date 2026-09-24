from sentence_transformers import SentenceTransformer, util
import os

model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
notes_dir = 'D:/obsidian/poosa/个人ai知识库/wiki'

note_files = []
for fname in os.listdir(notes_dir):
    if fname.endswith('.md'):
        content = open(notes_dir + '/' + fname, encoding='utf-8').read()
        note_files.append((fname, content))

embeddings = model.encode([c for _, c in note_files])

keyword = '技能'
q_vec = model.encode(keyword)
scores = util.cos_sim(q_vec, embeddings)[0]
top_idx = scores.argsort(descending=True)[:2]

print('=== 第1步：关键词 ===')
print(keyword)
print()
print('=== 第2步：top_idx（最相似2篇的索引）===')
print(top_idx.tolist())
print()
print('=== 第3步：遍历 top_idx，每篇的取出过程 ===')
for i in top_idx:
    print(f'  i = {i}')
    print(f'    note_files[{i}]     = 元组(文件名, 内容)，文件名 = {note_files[i][0]}')
    print(f'    note_files[{i}][1]  = 内容，前40字 = {note_files[i][1][:40]}...')
print()
print('=== 第4步：join 之后的结果（前120字）===')
result = '\n\n'.join(note_files[i][1] for i in top_idx)
print(result[:120])
print()
print('=== 第5步：结果长度 ===')
print(f'{len(result)} 字')
