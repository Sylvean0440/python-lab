from sentence_transformers import SentenceTransformer, util

# 加载模型（第一次会下载，约 100MB）
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 编码三句话
s1 = model.encode('技能清单')
s2 = model.encode('我学到了什么')
s3 = model.encode('今天天气不错')

# 算相似度（越接近 1 越相似）
print('「技能清单」vs「我学到了什么」:', round(util.cos_sim(s1, s2).item(), 3))
print('「技能清单」vs「今天天气不错」:', round(util.cos_sim(s1, s3).item(), 3))
