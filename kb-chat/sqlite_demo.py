import sqlite3
import json
from pathlib import Path


# ① 连接数据库：文件放在本脚本旁边，不受终端工作目录影响。
db_path = Path(__file__).with_name("chat_demo_v2.db")

def init_db():
    connection = sqlite3.connect(db_path)
    # 新数据库直接创建完整的消息表；已有表不会被这条语句修改。
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                display_content TEXT,
                sources TEXT NOT NULL DEFAULT '[]'
            )
        """)
        # ② 兼容旧数据库：查询的是字段信息，每行的索引 1 是字段名。
        cursor = connection.execute("PRAGMA table_info(messages)")
        columns = [row[1] for row in cursor.fetchall()]

        if "display_content" not in columns:
            connection.execute(
                "ALTER TABLE messages ADD COLUMN display_content TEXT"
            )

        if "sources" not in columns:
            # 默认值给旧记录补上空来源，也供省略 sources 的 INSERT 使用。
            connection.execute(
                "ALTER TABLE messages ADD COLUMN sources TEXT NOT NULL DEFAULT '[]'"
            )
        connection.commit()
    finally:
        connection.close()


# 删除指定会话的消息，不删除表，也不影响其他会话。
def clear_messages(conversation_id):
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,)
        )
        connection.commit()
    finally:
        connection.close()


def save_turn(conversation_id,user_message,assistant_message):
    connection = sqlite3.connect(db_path)
    try:
        for message in [user_message,assistant_message]:
            sources = message.get('sources',[])
            if sources is None:
                sources = []

            sources_text = json.dumps(sources, ensure_ascii=False)

            connection.execute(
                '''
                INSERT INTO messages(
                conversation_id,role,content,display_content,sources
            )
            VALUES(?,?,?,?,?)
            ''',
            (
                conversation_id,
                message['role'],
                message['content'],
                message.get('display_content'),
                sources_text
            )

            )
        connection.commit()
    finally:
        connection.close()


# ③ 保存一条消息：默认 None 是函数参数规则，不是数据库默认值。
def save_message(
    conversation_id, role, content, display_content=None, sources=None
):
    # 没有提供来源时，用空列表统一表示“没有来源文件”。
    # 每次调用创建自己的列表，避免把可变列表作为参数默认值。
    if sources is None:
        sources = []

    # 列表不能直接作为 SQLite 参数；dumps 把列表转成 JSON 字符串。
    # ensure_ascii=False 让中文直接显示。
    sources_text = json.dumps(sources, ensure_ascii=False)
    connection = sqlite3.connect(db_path)

    try:
        connection.execute(
            """
                INSERT INTO messages (
                conversation_id, role, content, display_content, sources
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            # 五个值依次对应五个占位符。
            # 字符串、整数可直接保存；display_content 的 None 对应 SQL NULL。
            (conversation_id, role, content, display_content, sources_text)
        )
        connection.commit()
    finally:
        connection.close()


# ④ 读取一个会话：返回 Python 列表，里面每条消息是 Python 字典。
def load_messages(conversation_id):
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.execute(
            """
            SELECT role, content, display_content, sources
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            # 单元素元组需要括号内的逗号。
            (conversation_id,)
        )
        rows = cursor.fetchall()
        messages = []

        for row in rows:
            # 索引由上面的 SELECT 顺序决定，不是数据库表中固定的列号。
            # row[3] 是来源 JSON 字符串；loads 将它还原成 Python 列表。
            message = {
                "role": row[0],
                "content": row[1],
                "sources": json.loads(row[3])
            }

            # SQL NULL 读取后为 None。没有单独显示文本时，不添加这个键。
            # 这样页面的 get("display_content", message["content"]) 才能回退。
            # 空字符串也可能是有效显示文本，因此判断 is not None。
            # 后续再显示历史记录时，如果 display_content 是空字符串，也会显示,所以需要 is not None 判断。
            if row[2] is not None:
                message["display_content"] = row[2]

            messages.append(message)

        # 没有查询到记录时，循环不执行，返回空列表。
        return messages
    finally:
        connection.close()


# ⑤ 调用示例：只读取，反复运行不会重复插入消息。
#想测试完整保存时，取消下面两次调用的注释，运行一次后再注释回去。
# 每执行一次 save_message 都会新增一条记录，它没有自动去重功能。
#save_message(
    # 103, "user", "资料：SQLite 可以保存消息。\n问题：今天学什么？",
    # display_content="今天学什么？" )
#save_message(
   # 103, "assistant", "今天学习 SQLite。",
   #sources=["学习日志.md", "用户画像.md"]
#)

if __name__ == "__main__":
    init_db()
    print("已有会话：", load_messages(101))
    print("不存在的会话：", load_messages(999))
    print("完整字段示例：", load_messages(103))
