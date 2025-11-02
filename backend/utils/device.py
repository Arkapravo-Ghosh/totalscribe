"""Device detection and setup utilities."""
import torch
from utils.logger import logger


def get_device() -> str:
    """Detect and return the best available device (cuda, mps, or cpu)."""
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    logger.info(f"Using device: {device}")
    return device


def get_model_dtype(device: str) -> torch.dtype:
    """
    Get the appropriate dtype for the model based on device.

    Args:
        device: The device string ('cuda', 'mps', or 'cpu')

    Returns:
        torch.dtype: The appropriate dtype for the device
    """
    if device == "mps":
        # Use float32 on MPS to avoid precision issues
        dtype = torch.float32
        logger.info("Using float32 on MPS device to prevent precision issues")
    elif device == "cuda":
        # Use float16 on CUDA for memory efficiency
        dtype = torch.float16
        logger.info("Using float16 on CUDA device for memory efficiency")
    else:
        # Use float32 on CPU
        dtype = torch.float32
        logger.info("Using float32 on CPU device")

    return dtype
