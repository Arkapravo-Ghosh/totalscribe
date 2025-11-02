"""LLM service for chat response generation."""

import torch
import threading
from transformers import TextIteratorStreamer
from configs.settings import LLM_MAX_TOKENS, SOAP_SECTION_MAX_TOKENS
from utils.logger import logger
from services.model_manager import model_manager


def generate_chat_response_sync(
    chat_messages: list,
    max_new_tokens: int = LLM_MAX_TOKENS,
    section_mode: bool = False,
) -> str:
    """
    Synchronous chat response generation with streaming to console.

    Args:
        chat_messages: List of chat messages
        max_new_tokens: Maximum number of tokens to generate
        section_mode: Whether generating a SOAP section (uses different params)

    Returns:
        str: Generated response text
    """
    with model_manager.generation_lock:
        logger.info(
            f"[LLM] Received messages: {len(chat_messages)} messages, section_mode: {section_mode}"
        )

        # Format and tokenize the input
        inputs = model_manager.llm_tokenizer.apply_chat_template(
            chat_messages,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs = inputs.to(model_manager.device)

        mode_desc = "section generation" if section_mode else "general generation"
        logger.info(f"[LLM] Starting {mode_desc} with improved parameters")

        # Set up streamer for console output
        streamer = TextIteratorStreamer(
            model_manager.llm_tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        # Clear cache before generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            torch.mps.empty_cache()

        generated_tokens = []

        def run_generation():
            """Run the actual generation in a separate thread."""
            try:
                with torch.no_grad():
                    _ = model_manager.llm_model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=True,
                        temperature=0.6,
                        top_p=0.9,
                        top_k=50,
                        repetition_penalty=1.15,
                        streamer=streamer,
                        pad_token_id=model_manager.llm_tokenizer.pad_token_id,
                        eos_token_id=model_manager.llm_tokenizer.eos_token_id,
                    )
            except Exception as e:
                logger.error(f"[LLM] Generation error: {str(e)}")
                streamer.end()

        # Start generation in a separate thread
        generation_thread = threading.Thread(target=run_generation)
        generation_thread.start()

        # Collect tokens and print them to console as they arrive
        print("[LLM STREAMING] Starting token generation:")

        for piece in streamer:
            generated_tokens.append(piece)
            print(piece, end="", flush=True)

        print()  # Add newline after streaming is complete
        generation_thread.join()

        # Combine all generated tokens
        text = "".join(generated_tokens).strip()

        # Clear any potential caches after generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            torch.mps.empty_cache()

        logger.info(
            f"[LLM] Generation completed. Response length: {len(text)} characters"
        )
        return text
