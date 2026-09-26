# 知识库 MCP 服务器（Knowledge Base MCP Server）

一个用 Python 写的 **MCP（Model Context Protocol）服务器**，让任何支持 MCP 的 AI（DSH、Claude Code、Cursor 等）都能**语义搜索、读写你的 Obsidian 知识库**。

## ✨ 功能（6 个工具）

| 工具 | 作用 |
|---|---|
| `kb_search` | 语义搜索：按「意思」找最相关的笔记（向量检索） |
| `kb_read` | 读一篇笔记的全文 |
| `kb_write` | 写 / 覆盖一篇笔记 |
| `kb_add` | 新建一篇笔记 |
| `kb_list` | 列出知识库里所有笔记 |
| `kb_reindex` | 重建向量索引（手动改文件后） |

## 🛠 技术亮点

- **向量检索**：用 `SentenceTransformer`（bge-small-zh-v1.5）把笔记编码成向量，用**余弦相似度**做语义搜索——不是关键词匹配，而是「按意思找」。
- **MCP 协议**：`@server.tool()` 把函数注册成工具，通过 stdio 与 AI 客户端通信——**换语言不换协议**，任何 MCP 客户端都能用。
- **路径配置化**：路径从 `config.json` 读，代码机器无关，换电脑只改配置、不动代码。
- **索引持久化**：编码结果缓存到 `index.json`，启动时直接读缓存，避免每次重新编码。
- **写完自动重建索引**：写 / 新建笔记后自动更新索引，无需手动刷新。

## 🚀 怎么跑

1. 装依赖：

   ```bash
   pip install mcp sentence-transformers
   ```

2. 复制配置模板，填你的笔记库路径：

   ```bash
   cp config.example.json config.json   # 然后改里面的路径
   ```

3. 启动：

   ```bash
   python kb_server.py
   ```

## 🔌 怎么接入 AI

在任意支持 MCP 的客户端里，把服务器启动命令配成：

```
python kb_server.py
```

（stdio 传输，服务器自动监听标准输入输出）
