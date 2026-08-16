from utils.ai_helper import generate_reply
ctx = [{'source':'property','id':1,'text':'Property 1: address 123 Main St: purchasePrice=300000, propertyValue=350000, weeklyRent=500'}]
print(generate_reply('list properties', ctx))
print('---')
print(generate_reply('what is the weekly rent for 123 main', ctx))
