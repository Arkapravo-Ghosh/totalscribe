"""Application settings and configuration."""

import os

# Cache and model directories
CACHE_DIR = "./cache"
MODEL_DIR = "./models"

# Ensure directories exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Environment variables for transformers (using HF_HOME as per v5 standard)
os.environ["HF_HOME"] = MODEL_DIR

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
]

# Model names
WHISPER_MODEL_NAME = "openai/whisper-large"
LLM_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

# Audio processing settings
CHUNK_DURATION = 10  # seconds
OVERLAP_DURATION = 1  # seconds
SAMPLE_RATE = 16000  # Hz
MAX_OVERLAP_CHARS = 80

# LLM generation settings
LLM_MAX_TOKENS = 1500
SOAP_SECTION_MAX_TOKENS = 800

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(CACHE_DIR, "soap_processing.log")
