# test_agent.py
from llm import LLMProxy

proxy = LLMProxy(llm_model="llama3.1", embedding_model="nomic-embed-text")
proxy.create_agent()

# test query
response = proxy.handle_complex_query("How to open the lamp in living room")
print(response)