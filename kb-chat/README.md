# 知识库网页助手

使用 Streamlit 提供网页入口，检索本地笔记后调用 DeepSeek 回答问题。

## 本机启动

在 PowerShell 中执行：

```powershell
cd C:\Users\Sylvean\Desktop\python-lab\kb-chat
python -m streamlit run app.py
```

或者在 `python-lab` 目录执行 `python -m streamlit run kb-chat/app.py`。
打开终端显示的 Local URL（通常为 `http://localhost:8501`）。保持终端运行，按 Ctrl+C 停止服务器。

本机 Python 需要安装 `streamlit`、`sentence-transformers` 和 `requests`。
应用从 `C:\Users\Sylvean\.dsh\.credentials.yaml` 读取 `DEEPSEEK_API_KEY`，从本目录 `config.json` 的 `vaultDir` 读取知识库路径。配置格式参考 `config.example.json`，目标知识库需包含有 Markdown 笔记的 `wiki` 目录。`config.json` 不提交到仓库。

## 已实现功能

- 检索笔记并回答问题。
- 同一网页会话中承接前文，并显示历史对话。
- 点击“发送”提交问题；普通页面重跑不会自动重复请求。
- 点击“清空会话”移除旧问题与回答，保留系统提示。
- 用户聊天气泡只显示原始问题；检索资料仍会发送给模型。

## 历史与缓存

聊天历史保存在当前网页会话的 `st.session_state` 中，没有写入文件或数据库。服务器停止或会话重建后不能依靠它恢复历史。

首次打开页面时，资源和数据缓存尚未建立，需要加载向量模型、读取笔记并编码，因此较慢。后续缓存有效时可复用模型和编码结果。修改笔记后，缓存不一定自动更新。

## 已验证与限制

2026-10-06 用户运行验证：用户气泡不显示检索资料；两轮追问能够承接；清空后聊天移除且新对话不再承接临时代号。源码语法检查通过。

当前每轮检索资料会随历史累积，尚未限制历史长度；API 请求尚未设置超时或失败恢复。应用使用本机路径配置，尚非可直接公开部署的版本。
