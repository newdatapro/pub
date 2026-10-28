import ollama
from openai import OpenAI

# 1. Source Context (Your data)
documents = ["AI Solutions Engineer focuses on federal compliance, health systems integration, and scalable pipelines."]
query = "What does an AI Solutions Engineer do?"

# 2. Naive Retrieval / Match
context = " ".join([doc for doc in documents if "AI Solutions Engineer" in doc])

# 3. Augment & Generate Prompt
prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer based only on the context provided."

# 4. Local Execution via Ollama (e.g., Llama 3.2 or Mistral)
response = ollama.generate(model="llama3.2", prompt=prompt)
print(response['response'])
