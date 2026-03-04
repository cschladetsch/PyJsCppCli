import anthropic, os
c = anthropic.Anthropic(api_key=os.environ['CLAUDE_API_KEY'])
r = c.messages.create(model='claude-3-5-sonnet-20241022', max_tokens=10, messages=[{'role':'user','content':'hi'}])
print(r.content[0].text)
