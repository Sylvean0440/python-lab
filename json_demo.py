import json

sources = ["学习日志.md", "用户画像.md"]

sources_text = json.dumps(sources, ensure_ascii=False)
print(sources_text)
print(type(sources_text))

restored_sources = json.loads(sources_text)
print(restored_sources)
print(type(restored_sources))
print(sources_text[0])
print(restored_sources[0])