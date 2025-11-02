"""Resource cleanup services."""

import os
import gc
import torch
import threading
import atexit
from utils.logger import logger
from utils.storage import visits_store


# Global cleanup flag with threading lock
_cleanup_done = False
_cleanup_lock = threading.Lock()


def cleanup_resources():
    """Clean up model resources and torch cache to prevent resource leaks."""
    global _cleanup_done

    with _cleanup_lock:
        if _cleanup_done:
            return
        _cleanup_done = True

    logger.info("Starting resource cleanup...")

    try:
        # Clear visits store first (fast)
        visits_store.clear()

        # Clear GPU caches (fast)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            torch.mps.empty_cache()

        # Clear model references (fast)
        from services.model_manager import model_manager

        try:
            del model_manager.whisper_model
            del model_manager.whisper_processor
            del model_manager.llm_model
            del model_manager.llm_tokenizer
        except Exception:
            pass

        # Single garbage collection (instead of 3)
        gc.collect()

        logger.info("Resource cleanup completed")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def full_cleanup_resources():
    """Complete cleanup for atexit - can take longer."""
    if _cleanup_done:
        return

    logger.info("Starting full resource cleanup...")

    try:
        # Do the fast cleanup first
        cleanup_resources()

        # Now do the slower operations
        # Clean up librosa cache
        try:
            import librosa

            librosa.cache.clear()
        except Exception:
            pass

        # Clean up multiprocessing resources
        try:
            import multiprocessing

            multiprocessing.active_children()
        except Exception:
            pass

        # Clean up threads with shorter timeout
        for thread in threading.enumerate():
            if thread != threading.current_thread() and hasattr(thread, "join"):
                try:
                    thread.join(timeout=0.5)
                except Exception:
                    pass

        # Additional garbage collections for thorough cleanup
        for _ in range(2):
            gc.collect()

        logger.info("Full resource cleanup completed")

    except Exception as e:
        logger.error(f"Error during full cleanup: {e}")


# Register full cleanup function to run at exit
atexit.register(full_cleanup_resources)
