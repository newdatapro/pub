# pub
There are multiple projects, each in its own project folder.  The goad is to keep each project completely self-contained with its own dependencies, and making it easy for anyone to clone and run them.

Please do not commit your .venv.  Virtual environments are platform-specific, contain absolute machine paths.  Store the dependency definition files (pyproject.toml or requirements.txt) in each project folder so users can instantly generate their own .venv locally.

## Project folders


ai-RAG has RAG related code

ai-genAI has generative AI code

av has code on Video to MP3 batch converter

