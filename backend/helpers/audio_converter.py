"""Audio conversion utilities using FFmpeg."""

import os
import subprocess
from utils.logger import logger


def check_ffmpeg_availability() -> bool:
    """Check if FFmpeg is available in the system PATH."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def convert_to_wav_with_ffmpeg(input_file: str, visit_id: str) -> str:
    """
    Convert any audio/video file to WAV format using FFmpeg.

    Args:
        input_file: Path to the input audio/video file
        visit_id: Visit ID for logging purposes

    Returns:
        str: Path to the converted WAV file

    Raises:
        Exception: If conversion fails
    """
    try:
        # Check if FFmpeg is available
        if not check_ffmpeg_availability():
            raise Exception("FFmpeg is not installed or not available in system PATH")

        # Create a temporary WAV file
        from configs.settings import CACHE_DIR

        wav_filename = f"{visit_id}_converted.wav"
        output_path = os.path.join(CACHE_DIR, wav_filename)

        # Remove existing converted file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)

        logger.info(
            f"Visit {visit_id}: Converting {input_file} to WAV format using FFmpeg"
        )

        # FFmpeg command to convert to WAV with specific parameters
        # -i: input file
        # -acodec pcm_s16le: use 16-bit PCM encoding
        # -ar 16000: set sample rate to 16kHz (optimal for Whisper)
        # -ac 1: convert to mono
        # -y: overwrite output file if it exists
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            input_file,
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-y",
            output_path,
        ]

        # Run FFmpeg conversion
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode != 0:
            raise Exception(f"FFmpeg conversion failed: {result.stderr}")

        # Verify the output file was created and has content
        if not os.path.exists(output_path):
            raise Exception("FFmpeg conversion produced no output file")

        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception("FFmpeg conversion produced an empty file")

        logger.info(
            f"Visit {visit_id}: Successfully converted to WAV format ({file_size} bytes)"
        )
        return output_path

    except subprocess.TimeoutExpired:
        logger.error(f"Visit {visit_id}: FFmpeg conversion timed out after 5 minutes")
        raise Exception(
            "Audio conversion timed out - file may be too large or corrupted"
        )
    except FileNotFoundError:
        logger.error(f"Visit {visit_id}: FFmpeg not found in system PATH")
        raise Exception(
            "FFmpeg is not installed or not found in system PATH. Please install FFmpeg to support various audio/video formats."
        )
    except Exception as e:
        logger.error(f"Visit {visit_id}: Error during FFmpeg conversion: {str(e)}")
        raise Exception(f"Failed to convert audio file: {str(e)}")
