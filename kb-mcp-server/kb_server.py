# kb_server.py —— 你的 MCP 服务器（Python 版，教学用）
import numpy as np
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'   # 国内镜像（huggingface 被墙时用，先设置再加载模型）

import json
from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer, util   # 向量检索的库（你昨天学的！）

# ============ ① 读配置：路径从 config.json 读（机器无关、不跨机）============
config = json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'), encoding='utf-8'))
WIKI_DIR = os.path.join(config['vaultDir'], 'wiki')   # 笔记目录 = vaultDir + wiki
INDEX_FILE = config['indexFile']




# ============ ② 创建服务器 ============
server = FastMCP("obsidian-knowledge-base")

# ============ ③ 向量检索准备 ============
# 模型名用 Python 的 'BAAI/...'（config.json 里的 'Xenova/...' 是 JS 版专用，不通用）
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

def load_notes():
    """读所有笔记 + 编码成向量，返回 (note_files, embeddings)"""
    note_files = []
    for fname in os.listdir(WIKI_DIR):
        if fname.endswith('.md'):
            content = open(os.path.join(WIKI_DIR, fname), encoding='utf-8').read()
            note_files.append((fname, content))
    embeddings = model.encode([c for _, c in note_files])
    return note_files, embeddings  


def save_index():
    """把 note_files 和 embeddings 一起存进 index.json"""
    data = {
        'note_files': note_files,
        'embeddings': [v.tolist() for v in embeddings],   # numpy → 普通列表
    }
    json.dump(data, open(INDEX_FILE, 'w', encoding='utf-8'))   # 一次写进去


def load_index():
    """从 index.json 读回；没文件或读失败就返回 None"""
    try:
        data = json.load(open(INDEX_FILE, encoding='utf-8'))
        note_files = data['note_files']
        embeddings = [np.array(v) for v in data['embeddings']]   # 普通列表 → numpy
        return note_files, embeddings
    except:
        return None   # 没文件 / JS 版格式读不了，都返回 None → 触发重建
    

def refresh_index():
    """重新扫描 + 重新编码，更新全局的 note_files 和 embeddings"""
    global note_files, embeddings
    note_files, embeddings = load_notes()
    save_index()   # ← 加这行：编码完存起来


loaded = load_index()                    # ① 先试着读缓存
if loaded:                               # ② 读到了（不是 None）
    note_files, embeddings = loaded      #    直接用缓存 → 秒开
else:                                    # ③ 没读到
    note_files, embeddings = load_notes()#    第一次编码（慢）
    save_index()                         #    存起来，下次就快


# ============ ④ 工具 kb_list：列出所有笔记 ============
@server.tool()
def kb_list() -> str:
    """列出知识库里所有笔记的文件名"""
    files = [f for f in os.listdir(WIKI_DIR) if f.endswith(".md")]
    return "\n".join(files)

# ============ ⑤ 工具 kb_read：读一篇笔记 ============
@server.tool()
def kb_read(path: str) -> str:
    """读一篇笔记的全文。path 是相对路径，比如 '记忆索引.md'"""
    full = os.path.join(WIKI_DIR, path)
    with open(full, encoding="utf-8") as f:
        return f.read()

# ============ ⑥ 工具 kb_write：写/覆盖一篇笔记 ============
@server.tool()
def kb_write(path: str, content: str) -> str:
    """写或覆盖一篇笔记。path 是相对路径（如 '测试.md'），content 是完整内容。"""
    full = os.path.join(WIKI_DIR, path)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    refresh_index()   # 写完自动重建索引，让新内容能被搜到
    return f"已写入：{path}"

# ============ ⑦ 工具 kb_add：新建一篇笔记 ============
@server.tool()
def kb_add(title: str, content: str) -> str:
    """新建一篇笔记。title 是标题（会自动作为文件名），content 是内容。"""
    safe = title.strip().replace("/", " ").replace("\\", " ")
    full = os.path.join(WIKI_DIR, safe + ".md")
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    refresh_index()   # 建完自动重建索引
    return f"已新建：{safe}.md"

# ============ ⑧ 工具 kb_search：语义搜索（你昨天学的向量检索！）============
@server.tool()
def kb_search(query: str, top_k: int = 3) -> str:
    """语义搜索知识库，返回最相关的笔记。query 是搜索问题，top_k 是返回篇数（默认3）。"""
    q_vec = model.encode(query)                        # ① 问题 → 向量
    scores = util.cos_sim(q_vec, embeddings)[0]        # ② 和每篇笔记算相似度
    top_idx = scores.argsort(descending=True)[:top_k]  # ③ 取最相似的 top_k 篇的索引
    return "\n\n".join(note_files[i][1] for i in top_idx)

# ============ ⑨ 工具 kb_reindex：重建索引 ============
@server.tool()
def kb_reindex() -> str:
    """重新扫描知识库并重建向量索引（手动改文件后调用）。"""
    refresh_index()    # 重新扫描 + 重新编码
    return f"已重建索引：{len(note_files)} 篇笔记"

# ============ ⑩ 启动服务器 ============
if __name__ == "__main__":
    server.run()
