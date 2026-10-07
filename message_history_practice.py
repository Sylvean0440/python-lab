def add_message(messages, role, content):
    # 把一条消息追加到传入的历史列表
    messages.append({'role': role, 'content':content})



def clear_messages():
    # 创建并返回一份新的会话列表，只保留 system
    return[{'role': 'system', 'content':'你是一个助手'}]


messages = clear_messages()

add_message(messages, 'user', '我叫小林')
add_message(messages, 'assistant', '你好，小林！')
add_message(messages, 'user', '我叫什么名字？')

print('第二轮发送前：')
print('消息数量',len(messages))
for message in messages:
    print(message['role'],':',message['content'])

user_questions = []

for message in messages:
    if message['role'] == 'user':
        user_questions.append(message['content'])

print(user_questions)


messages = clear_messages()

print('清空后：')
print('消息数量',len(messages))
for message in messages:
    print(message['role'],':',message['content'])


api_messages = []
api_messages.append(messages[0])
api_messages.extend(messages[1:7])
