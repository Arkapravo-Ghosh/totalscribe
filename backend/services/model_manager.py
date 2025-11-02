"""Model loading and management."""

import torch
import threading
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoTokenizer,
    AutoModelForCausalLM,
)
from configs.settings import WHISPER_MODEL_NAME, LLM_MODEL_NAME
from utils.device import get_device, get_model_dtype
from utils.logger import logger


class ModelManager:
    """Manages ML models for the application."""

    def __init__(self):
        self.device = get_device()
        self.generation_lock = threading.Lock()

        # Whisper model components
        self.whisper_processor = None
        self.whisper_model = None

        # LLM model components
        self.llm_tokenizer = None
        self.llm_model = None
        self.llm_model_dtype = None

        self._load_models()

    def _load_models(self):
        """Load all required models."""
        logger.info("Loading Whisper model...")
        self._load_whisper_model()

        logger.info("Loading LLM model...")
        self._load_llm_model()

        logger.info("All models loaded successfully")

    def _load_whisper_model(self):
        """Load Whisper model for speech-to-text."""
        self.whisper_processor = WhisperProcessor.from_pretrained(WHISPER_MODEL_NAME)
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained(
            WHISPER_MODEL_NAME, dtype=torch.float32
        ).to(self.device)
        logger.info(f"Whisper model loaded on {self.device}")

    def _load_llm_model(self):
        """Load LLM model for SOAP note generation."""
        self.llm_tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)

        # Get appropriate dtype for the device
        self.llm_model_dtype = get_model_dtype(self.device)

        # Load model with appropriate dtype
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_NAME,
            dtype=self.llm_model_dtype,
        )
        self.llm_model.to(self.device)
        self.llm_model.config.dtype = self.llm_model_dtype
        self.llm_model.eval()

        # Ensure proper tokenizer setup
        if self.llm_tokenizer.pad_token is None:
            self.llm_tokenizer.pad_token = self.llm_tokenizer.eos_token
        self.llm_model.config.pad_token_id = self.llm_tokenizer.pad_token_id

        logger.info(
            f"LLM model loaded: {LLM_MODEL_NAME} on {self.device} with dtype {self.llm_model_dtype}"
        )


# Global model manager instance
model_manager = ModelManager()
