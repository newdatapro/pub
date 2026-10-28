from openai import OpenAI, APIConnectionError, APIStatusError
from pathlib import Path
import shutil
import json
import logging
import sys
from typing import Dict, Any

# =====================================================================
# LOGGING CONFIGURATION
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PipelineWorkflow")

CONFIG_FILENAME = "openai-multi-steps-response-config.json"


# =====================================================================
# CONFIGURATION LOADER WITH VALIDATION
# =====================================================================
def load_config(config_path: str = CONFIG_FILENAME) -> Dict[str, Any]:
    """
    Loads configuration from a JSON file. Creates a default template 
    if the file does not exist, and handles parsing errors gracefully.
    """
    path = Path(config_path)
    default_config = {
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",
        "fallback_model": "qwen2.5-14b-instruct",
        "org_path": "/Volumes/TP-Share/self/profile/applied/zstaging/JD.org.txt",
        "target_path": "/Volumes/TP-Share/self/profile/applied/zstaging/JD.txt",
        "temperature": 0.7
    }

    if not path.exists():
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            logger.info(f"Created default configuration file at: {path.absolute()}")
        except IOError as e:
            logger.error(f"Failed to create default config file: {e}")
            sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in {config_path}: {e}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"Could not read config file {config_path}: {e}")
        sys.exit(1)

    # Validate required keys
    required_keys = ["base_url", "api_key", "fallback_model", "org_path", "target_path", "temperature"]
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration key: '{key}' in {config_path}")
            sys.exit(1)

    # Convert paths
    config["org_path"] = Path(config["org_path"])
    config["target_path"] = Path(config["target_path"])
    return config


CONFIG = load_config()

# =====================================================================
# CLIENT & MODEL INITIALIZATION
# =====================================================================
try:
    client = OpenAI(
        base_url=CONFIG["base_url"],
        api_key=CONFIG["api_key"]
    )
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    sys.exit(1)


def get_active_model() -> str:
    """Attempts to retrieve the active model ID from LM Studio, falls back otherwise."""
    try:
        models = client.models.list()
        if models.data:
            model_id = models.data[0].id
            logger.info(f"Detected active model from server: {model_id}")
            return model_id
    except Exception as e:
        logger.warning(f"Could not fetch active models list ({e}). Using fallback.")
    
    return CONFIG["fallback_model"]


LOCAL_MODEL = get_active_model()


# =====================================================================
# CORE UTILITIES
# =====================================================================
def call_local_llm(prompt: str) -> str:
    """
    Executes a chat completion request against the local LM Studio instance
    with professional error handling.
    """
    logger.info(f"Calling local model [{LOCAL_MODEL}]...")
    try:
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=CONFIG["temperature"]
        )
        return response.choices[0].message.content
    except APIConnectionError as e:
        logger.error(f"Failed to connect to LM Studio server at {CONFIG['base_url']}.")
        logger.error("Make sure LM Studio server is running (`lms server start`). Details: %s", e)
        raise
    except APIStatusError as e:
        logger.error(f"LM Studio API returned a non-200 status code: {e.status_code} - {e.response}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during LLM invocation: {e}")
        raise


def execute_step(step_number: int, step_title: str, prompt: str, target_path: Path) -> str:
    """
    Executes a pipeline step: queries LLM, logs output,
    and safely appends the response to the target file.
    """
    logger.info(f"--- STEP {step_number}: {step_title} ---")
    response_text = call_local_llm(prompt)
    logger.info(f"Received response for Step {step_number} ({len(response_text)} characters).")
    
    try:
        with open(target_path, "a", encoding="utf-8") as file:
            file.write(f"\n\n--- Response {step_number} ({step_title}) ---\n{response_text}")
    except IOError as e:
        logger.error(f"Failed to write response to target file {target_path}: {e}")
        raise

    return response_text


# =====================================================================
# MULTI-STEP PIPELINE WORKFLOW
# =====================================================================
def run_multi_step_workflow() -> None:
    logger.info(f"=== STARTING LOCAL MULTI-STEP PIPELINE ({LOCAL_MODEL}) ===")

    target_path = CONFIG["target_path"]
    org_path = CONFIG["org_path"]
    
    # Input validation for source file
    if not org_path.exists():
        logger.error(f"Source Job Description file not found at: {org_path}")
        sys.exit(1)

    try:
        if target_path.exists():
            target_path.unlink()
        
        # Ensure parent directories exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(org_path, target_path)
        logger.info(f"Copied source JD to target path: {target_path}")
    except IOError as e:
        logger.error(f"File operation failed during setup: {e}")
        sys.exit(1)

    try:
        with open(target_path, "r", encoding="utf-8") as file:
            JD = file.read()
    except IOError as e:
        logger.error(f"Failed to read target file {target_path}: {e}")
        sys.exit(1)

    if not JD.strip():
        logger.error("The Job Description file is empty. Aborting pipeline.")
        sys.exit(1)

    try:
        # Step 1: Extract Core Info
        prompt_step1 = f"""
        Extract ONLY the company name from the following job description. 
        Extract ONLY the Job title from the following job description.
        Extract ONLY the salary.
        Do not include any intro, explanation, bullets, or extra text. Output nothing but the company name, Job title, salary.
        Job Description:
        {JD}
        """
        _ = execute_step(1, "Company, Title & Salary", prompt_step1, target_path)

        # Step 2: Extract Verbs and Nouns
        prompt_step2 = f"""
        Please create a list of action verbs and proper nouns based on sections in Responsibilities, Qualifications of JD.txt.
        ---
        {JD}
        ---
        """
        verbs_and_nouns = execute_step(2, "Generating Verbs and Nouns", prompt_step2, target_path)

        # Step 3: Products and Services
        prompt_step3 = f"""
        Based on the extracted keywords and nouns:
        {verbs_and_nouns}
        
        List potential latest products and services from this company aligning to this role.
        """
        role_products_and_services = execute_step(3, "Products and Services", prompt_step3, target_path)

        # Step 4: Initial STAR Mock Questions
        prompt_step4 = f"""
        Based on the Responsibilities and Qualifications of the Job Description:\n'{JD}'\n\n
        Come up with 3 5-minute mock interview questions and responses in STAR format for this role.
        Emphasize a specific technology stack from the resume with signals of the role.
        Create a sense of urgency to the situation, difficulty of the task, swift and decisive actions, and results beyond expectations.        
        Use short sentences.
        """
        mock_initial = execute_step(4, "Initial STAR Mocks", prompt_step4, target_path)

        # Step 5: Refine Mocks using Products & Services context
        prompt_step5 = f"""
        Based on the Products and Services of this role: '{role_products_and_services}'\n\n
        Refine the previous mock interview questions and responses in STAR format to directly address these products/services.
        
        Previous Mocks to Refine:
        {mock_initial}
        """
        _ = execute_step(5, "Mocks Refined with Products & Services", prompt_step5, target_path)

        logger.info("=== WORKFLOW COMPLETE SUCCESSFULLY ===")

    except Exception as e:
        logger.error(f"Pipeline failed midway due to an exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_multi_step_workflow()
