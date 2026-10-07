# -*- coding: utf-8 -*-
"""
亲手验证：词 → 向量（embedding）
目标：亲眼看到"意思相近的词，向量也相近"——你刚学的那条性质。

用到的知识（都能对上你学的）：
1. embedding = 把词变成高维向量
2. 余弦相似度 = 去掉长度的点积 = 量"两个向量方向多一致"
   （normalize_embeddings=True 会让向量长度=1，此时 点积 = 余弦相似度）
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# 1. 加载模型（bge-small-zh-v1.5：你 RAG 里把文本变成向量的那个）
#    local_files_only=True = 只读本地缓存、不联网（HuggingFace 被墙，联网会卡死重试）
print("加载模型...")
model = SentenceTransformer("BAAI/bge-small-zh-v1.5", local_files_only=True)

# 2. 要测的词
words = ["猫", "狗", "汽车", "苹果", "香蕉", "电脑"]

# 3. 把每个词变成向量（bge-small 是 512 维）
vectors = model.encode(words, normalize_embeddings=True)

print(f"每个词变成了 {vectors.shape[1]} 维的向量\n")

# 4. 打印相似度矩阵（点积 = 余弦相似度，因为已归一化）
print("相似度矩阵（越接近 1 越像，越接近 0 越无关）：\n")
print("        " + "".join(f"{w:>8}" for w in words))
for i, w1 in enumerate(words):
    row = [float(np.dot(vectors[i], vectors[j])) for j in range(len(words))]
    print(f"{w1:<7}" + "".join(f"{v:>8.3f}" for v in row))

# 5. 结论
print("\n结论：")
print(f"  猫 vs 狗    相似度 = {float(np.dot(vectors[0], vectors[1])):.3f}  ← 都是动物，应该高")
print(f"  猫 vs 汽车  相似度 = {float(np.dot(vectors[0], vectors[2])):.3f}  ← 无关，应该低")
print(f"  苹果 vs 香蕉 相似度 = {float(np.dot(vectors[3], vectors[4])):.3f}  ← 都是水果，应该高")
print(f"  苹果 vs 电脑 相似度 = {float(np.dot(vectors[3], vectors[5])):.3f}  ← 无关，应该低")
