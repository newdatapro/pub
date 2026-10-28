# Local RAG Pipeline with Ollama

In this folder the rag_basic.py is the bare minimal version.  The rag_basic_errorhandling.py adds error handling for production ready.

Both are lightweight, local Retrieval-Augmented Generation (RAG) pipeline built with Python and [Ollama](https://ollama.com/). This project uses local context retrieval and grounding to deliver accurate, context-bound LLM responses without relying on external cloud APIs.

## Features

- **Privacy-First Inference:** Runs entirely locally via Ollama (e.g., `llama3.2`).
- **Grounded Responses:** Enforces context-only answers to minimize hallucinations.
- **Robust Error Handling:** Built-in safeguards for API timeouts, missing server connections, and schema validation.
- **Production-Ready Logging:** Uses Python's native `logging` module for auditability and debugging.

## Prerequisites

- **Python:** 3.8 or higher
- **Ollama:** Installed and running locally ([Download Ollama](https://ollama.com/))
- **Model:** Pull the target model prior to running:
  ```bash
  ollama pull llama3.2
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Install dependencies:
   ```bash
   pip install ollama
   ```

## Usage

Ensure your local Ollama instance is active, then execute the main pipeline:

```bash
python main.py
```

### Example Code Snippet

```python
from main import generate_rag_response

documents = [
    "AI Solutions Engineer focuses on federal compliance, health systems integration, and scalable pipelines."
]
query = "What does an AI Solutions Engineer do?"

response = generate_rag_response(documents=documents, query=query, model_name="llama3.2")
print(response)
```

## Configuration

You can customize execution parameters inside `main.py`:
- **Model Selection:** Default is `llama3.2`. Change the `model_name` argument to use `mistral`, `llama3`, or other installed local models.
- **Logging Level:** Modify `logging.basicConfig(level=logging.INFO)` to adjust output verbosity.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
