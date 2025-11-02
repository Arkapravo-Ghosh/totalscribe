"""Audio transcription service using Whisper."""

import os
import asyncio
import torch
import librosa
import soundfile as sf
from helpers.audio_converter import convert_to_wav_with_ffmpeg
from helpers.text_utils import remove_overlap
from configs.settings import (
    CHUNK_DURATION,
    OVERLAP_DURATION,
    SAMPLE_RATE,
    MAX_OVERLAP_CHARS,
)
from utils.logger import logger
from utils.storage import visits_store
from services.model_manager import model_manager


async def transcribe_audio(file_path: str, visit_id: str) -> str:
    """
    Transcribe audio file using Whisper model.

    Args:
        file_path: Path to the audio file
        visit_id: Visit ID for tracking

    Returns:
        str: Transcribed text

    Raises:
        Exception: If transcription fails
    """
    try:
        # Update progress and start timing
        transcription_start_time = asyncio.get_event_loop().time()
        visits_store[visit_id]["status"] = "analyzing_audio"
        visits_store[visit_id]["progress"] = 10
        logger.info(
            f"Visit {visit_id}: Starting audio transcription from file: {file_path}"
        )

        # Load audio with FFmpeg conversion support
        converted_file_path = None
        try:
            audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
            logger.info(
                f"Visit {visit_id}: Audio loaded successfully with librosa. Duration: {len(audio) / sr:.2f}s"
            )

        except Exception as soundfile_error:
            logger.warning(
                f"Visit {visit_id}: librosa failed to load audio directly: {str(soundfile_error)}"
            )
            logger.info(f"Visit {visit_id}: Attempting FFmpeg conversion to WAV format")

            try:
                # Try converting with FFmpeg
                converted_file_path = convert_to_wav_with_ffmpeg(file_path, visit_id)

                # Now try loading the converted file
                audio, sr = librosa.load(converted_file_path, sr=SAMPLE_RATE)
                logger.info(
                    f"Visit {visit_id}: Audio loaded successfully after FFmpeg conversion. Duration: {len(audio) / sr:.2f}s"
                )

            except Exception as ffmpeg_error:
                logger.error(
                    f"Visit {visit_id}: FFmpeg conversion also failed: {str(ffmpeg_error)}"
                )
                logger.info(
                    f"Visit {visit_id}: Attempting final fallback with soundfile"
                )

                try:
                    # Final fallback: try soundfile directly
                    audio, sr = sf.read(file_path)
                    if sr != SAMPLE_RATE:
                        import scipy.signal

                        audio = scipy.signal.resample(
                            audio, int(len(audio) * SAMPLE_RATE / sr)
                        )
                        sr = SAMPLE_RATE
                    logger.info(
                        f"Visit {visit_id}: Audio loaded successfully with soundfile. Duration: {len(audio) / sr:.2f}s"
                    )
                except Exception as final_error:
                    logger.error(
                        f"Visit {visit_id}: All audio loading methods failed. Last error: {str(final_error)}"
                    )
                    raise Exception(
                        f"Failed to load audio file. Please ensure the file is a valid audio/video format. Error: {str(final_error)}"
                    )

        # Store audio duration
        visits_store[visit_id]["audio_duration"] = len(audio) / sr

        # Chunk settings
        chunk_length = CHUNK_DURATION * sr
        overlap_length = OVERLAP_DURATION * sr
        num_chunks = (len(audio) + chunk_length - 1) // (chunk_length - overlap_length)

        full_text = ""

        logger.info(
            f"Visit {visit_id}: Processing {num_chunks} audio chunks for transcription"
        )

        for i in range(num_chunks):
            start = i * (chunk_length - overlap_length)
            end = min(start + chunk_length, len(audio))
            chunk = audio[start:end]

            # Update progress tracking for this chunk
            visits_store[visit_id]["current_chunk"] = i + 1
            visits_store[visit_id]["total_chunks"] = num_chunks
            visits_store[visit_id]["chunk_status"] = "processing"

            # Progress calculation: 10% to 35% during transcription
            chunk_progress = 10 + int((i / num_chunks) * 25)
            visits_store[visit_id]["progress"] = chunk_progress

            logger.info(
                f"Visit {visit_id}: Processing chunk {i + 1}/{num_chunks} (Progress: {chunk_progress}%)"
            )

            # Process chunk with Whisper
            inputs = model_manager.whisper_processor(
                chunk, sampling_rate=sr, return_tensors="pt"
            )
            inputs = inputs.input_features.to(model_manager.device)

            # Generate transcription
            with torch.no_grad():
                predicted_ids = model_manager.whisper_model.generate(inputs)

            transcription = model_manager.whisper_processor.batch_decode(
                predicted_ids, skip_special_tokens=True
            )[0]

            # Remove overlap between chunks
            if full_text and transcription:
                transcription = remove_overlap(
                    full_text, transcription, MAX_OVERLAP_CHARS
                )

            full_text += " " + transcription
            visits_store[visit_id]["chunk_status"] = "completed"

            logger.info(
                f"Visit {visit_id}: Chunk {i + 1}/{num_chunks} completed. Chunk text length: {len(transcription)}"
            )

            # Small delay to allow SSE to send updates
            await asyncio.sleep(0.05)

        visits_store[visit_id]["status"] = "extracting_text"
        visits_store[visit_id]["progress"] = 40
        visits_store[visit_id]["transcript"] = full_text.strip()

        # Clean up ALL chunk processing fields after transcription completion
        chunk_fields_to_remove = [
            "current_chunk",
            "total_chunks",
            "chunk_status",
        ]
        for field in chunk_fields_to_remove:
            visits_store[visit_id].pop(field, None)

        # Calculate transcription time
        transcription_end_time = asyncio.get_event_loop().time()
        transcription_duration = transcription_end_time - transcription_start_time
        visits_store[visit_id]["transcription_time"] = transcription_duration

        logger.info(
            f"Visit {visit_id}: Transcription completed. Transcript length: {len(full_text)} characters, Duration: {transcription_duration:.2f}s"
        )

        # Clean up converted file if it was created
        if converted_file_path and os.path.exists(converted_file_path):
            try:
                os.remove(converted_file_path)
                logger.info(
                    f"Visit {visit_id}: Cleaned up converted audio file: {converted_file_path}"
                )
            except Exception as e:
                logger.warning(
                    f"Visit {visit_id}: Failed to clean up converted file: {str(e)}"
                )

        # Clean up original audio file after successful transcription
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(
                    f"Visit {visit_id}: Cleaned up original audio file: {file_path}"
                )
            except Exception as e:
                logger.warning(
                    f"Visit {visit_id}: Failed to clean up original audio file: {str(e)}"
                )

        # Small delay to allow SSE to send the clean status update without chunk info
        await asyncio.sleep(0.1)

        return full_text.strip()

    except Exception as e:
        # Clean up converted file if it was created and an error occurred
        if (
            "converted_file_path" in locals()
            and converted_file_path
            and os.path.exists(converted_file_path)
        ):
            try:
                os.remove(converted_file_path)
                logger.info(
                    f"Visit {visit_id}: Cleaned up converted file after error: {converted_file_path}"
                )
            except Exception as cleanup_e:
                logger.warning(
                    f"Visit {visit_id}: Failed to clean up converted file after error: {str(cleanup_e)}"
                )

        # Clean up original audio file even if transcription failed
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(
                    f"Visit {visit_id}: Cleaned up original audio file after error: {file_path}"
                )
            except Exception as cleanup_e:
                logger.warning(
                    f"Visit {visit_id}: Failed to clean up original audio file after error: {str(cleanup_e)}"
                )

        logger.error(f"Visit {visit_id}: Transcription failed - {str(e)}")
        raise Exception(f"Transcription failed: {str(e)}")
