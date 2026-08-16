from utils.ai_helper import build_context, generate_reply
ctx = build_context(1)
print('context entries:', len(ctx))
for c in ctx:
    print(c)
print('--- reply ---')
print(generate_reply('Is property profitable?', ctx))
