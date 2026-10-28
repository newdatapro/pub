# Local Multi-Step LLM Pipeline

A modular Python script that automates multi-step job application preparation (extracting key details, mapping skills, and generating STAR-format mock interview questions) using a local LM Studio instance.

## Features

- **Automated Workflow**: Sequentially processes Job Descriptions (JDs) through customized prompt steps.
- **Local LLM Integration**: Connects seamlessly with LM Studio via standard OpenAI API client interfaces.
- **External Configuration**: Keeps file paths, server endpoints, model choices, and generation settings in a JSON config.
- **Robust Error Handling**: Built-in validation for missing files, empty inputs, API connection failures, and file I/O operations.
- **Structured Logging**: Timestamped console output tracks pipeline execution in real time.

## Prerequisites

- Python 3.8+
- [LM Studio](https://lmstudio.ai/) running locally (`lms server start`) with an active model loaded.

## Installation

1. Clone or download the repository.
2. Install required dependencies:

```bash
pip install openai
