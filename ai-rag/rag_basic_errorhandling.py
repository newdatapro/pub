import logging
from typing import List
import ollama

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def retrieve_context(documents: List[str], query: str) -> str:
    """
    Performs a naive keyword-based retrieval from the provided documents.
    """
    try:
        # Extract keywords from the query for naive matching (e.g., matching 'AI Solutions Engineer')
        # In a real pipeline, you would use semantic search/embeddings here.
        matched_docs = [doc for doc in documents if any(word in doc for word in query.split() if len(word) > 3)]
        
        # Fallback to general documents if strict keyword match fails, or keep empty
        if not matched_docs:
            logger.warning("No direct keyword match found in documents. Proceeding with full document set as fallback.")
            matched_docs = documents

        context = " ".join(matched_docs)
        return context
    except Exception as e:
        logger.error(f"Error during context retrieval: {e}")
        raise

def generate_rag_response(documents: List[str], query: str, model_name: str = "llama3.2") -> str:
    """
    Generates a response using Ollama based on the provided documents and query,
    with built-in error checking and input validation.
    """
    # 1. Input Validation
    if not documents:
        raise ValueError("The documents list cannot be empty.")
    if not query.strip():
        raise ValueError("The query cannot be empty.")

    # 2. Source Context Retrieval
    logger.info("Retrieving context from documents...")
    context = retrieve_context(documents, query)
    
    if not context.strip():
        return "Error: No relevant context could be established to answer the query."

    # 3. Augment & Generate Prompt
    prompt = (
        f"Context: {context}\n\n"
        f"Question: {query}\n"
        f"Answer based only on the context provided. If the answer cannot be found "
        f"in the context, state 'I cannot find the answer in the provided documents.'"
    )

    # 4. Local Execution via Ollama with Error Handling
    logger.info(f"Sending request to Ollama model: {model_name}...")
    try:
        response = ollama.generate(model=model_name, prompt=prompt)
        
        # Validate response structure
        if not response or 'response' not in response:
            raise ValueError("Received an invalid response structure from the Ollama server.")
            
        return response['response'].strip()
        
    except ollama.ResponseError as e:
        logger.error(f"Ollama API error occurred: {e.error} (Status Code: {e.status_code})")
        return f"Error: Failed to generate response due to an Ollama service error."
    except ConnectionError as e:
        logger.error(f"Failed to connect to the local Ollama instance. Is the server running? Details: {e}")
        return "Error: Could not connect to Ollama. Please ensure the local Ollama service is running."
    except Exception as e:
        logger.error(f"An unexpected error occurred during generation: {e}")
        return "Error: An unexpected error occurred while processing your request."

# --- Execution Entrypoint ---
if __name__ == "__main__":
    # Source Context Data
    sample_documents = [
        "AI Solutions Engineer focuses on federal compliance, health systems integration, and scalable pipelines."
    ]
    sample_query = "What does an AI Solutions Engineer do?"

    try:
        answer = generate_rag_response(documents=sample_documents, query=sample_query)
        print("\n--- Generated Answer ---")
        print(answer)
    except Exception as err:
        logger.critical(f"Pipeline execution failed: {err}")
