from ollama import chat
from ollama import ChatResponse
import time


response: ChatResponse = chat(model='llama3.1', messages=[
  {
    'role': 'user',
    'content': 'Re write this in Hindi: My name is Hemang',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)

