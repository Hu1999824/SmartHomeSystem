# test_ollama.py
import os
from langchain_ollama import ChatOllama


print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

llm = ChatOllama(model="qwen3-vl:2b", temperature=0.0)

try:
    resp = llm.invoke("Hello, are you working?")
    print("✅ success:", resp.content)
except Exception as e:
    import traceback
    print("❌ failed:")
    traceback.print_exc()