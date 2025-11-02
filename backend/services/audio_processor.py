"""Audio processing pipeline service."""

import asyncio
from services.transcription import transcribe_audio
from services.soap_generator import generate_soap_note
from utils.logger import logger
from utils.storage import visits_store


async def process_audio_file(audio_file_path: str, visit_id: str):
    """
    Async function to process audio file for SOAP note generation.
    This function runs without await (fire-and-forget) and updates progress.

    Args:
        audio_file_path: Path to the audio file
        visit_id: Visit ID for tracking
    """
    if visit_id not in visits_store:
        return

    try:
        # Update status to processing
        visits_store[visit_id]["status"] = "processing"
        visits_store[visit_id]["progress"] = 0
        logger.info(
            f"Visit {visit_id}: Starting audio processing pipeline for file: {audio_file_path}"
        )

        # Step 1: Transcribe audio using Whisper
        transcript = await transcribe_audio(audio_file_path, visit_id)

        if not transcript:
            raise Exception("Transcription produced empty result")

        # Store transcript for reference
        visits_store[visit_id]["transcript"] = transcript
        logger.info(
            f"Visit {visit_id}: Transcript stored with {len(transcript)} characters"
        )

        # Step 2: Generate SOAP note using Mistral
        logger.info(f"Visit {visit_id}: Starting SOAP note generation with Mistral LLM")
        llm_start_time = asyncio.get_event_loop().time()

        soap_note = await generate_soap_note(transcript, visit_id)

        llm_end_time = asyncio.get_event_loop().time()
        llm_duration = llm_end_time - llm_start_time
        logger.info(
            f"Visit {visit_id}: LLM generation completed in {llm_duration:.2f} seconds"
        )

        if not soap_note:
            raise Exception("SOAP note generation produced empty result")

        # Final completion
        visits_store[visit_id]["status"] = "finalizing"
        visits_store[visit_id]["progress"] = 95
        logger.info(f"Visit {visit_id}: Finalizing processing")

        visits_store[visit_id]["status"] = "completed"
        visits_store[visit_id]["progress"] = 100
        visits_store[visit_id]["soap_note"] = soap_note
        visits_store[visit_id]["generation_time"] = llm_duration

        logger.info(f"Visit {visit_id}: Processing completed successfully")

    except Exception as e:
        visits_store[visit_id]["status"] = "error"
        visits_store[visit_id]["error"] = str(e)
        logger.error(f"Visit {visit_id}: Processing failed - {str(e)}")

    logger.info(f"Visit {visit_id}: Audio processing pipeline finished")
