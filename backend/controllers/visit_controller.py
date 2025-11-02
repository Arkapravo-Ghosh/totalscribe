"""Visit controller for managing visit-related operations."""

import uuid
import asyncio
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from utils.storage import visits_store
from utils.logger import logger
from services.audio_processor import process_audio_file
from configs.settings import CACHE_DIR


async def create_visit():
    """
    Creates a new visit and returns a UUID visit ID.
    Stores the visit in the hashmap.
    """
    visit_id = str(uuid.uuid4())

    # Store visit in hashmap
    visits_store[visit_id] = {
        "id": visit_id,
        "status": "created",
        "progress": 0,
        "soap_note": None,
    }

    logger.info(f"Visit {visit_id}: New visit created")
    return JSONResponse(content={"visit_id": visit_id}, status_code=201)


async def process_soap_note(visit_id: str, audio_file: UploadFile):
    """
    Accepts an audio/video file for a specific visit ID and queues it for processing.
    Supports a wide variety of formats through FFmpeg conversion.
    Returns "queued" response immediately after starting async processing.
    """
    # Check if visit exists
    if visit_id not in visits_store:
        logger.warning(
            f"Visit {visit_id}: Audio upload attempted for non-existent visit"
        )
        raise HTTPException(status_code=404, detail="Visit not found")

    # Save uploaded file to cache directory
    audio_file_path = f"{CACHE_DIR}/{visit_id}_{audio_file.filename}"

    try:
        # Save the uploaded file
        with open(audio_file_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)

        # Update visit status
        visits_store[visit_id]["status"] = "queued"
        visits_store[visit_id]["audio_file_path"] = audio_file_path

        logger.info(
            f"Visit {visit_id}: Audio file uploaded successfully ({audio_file.filename}, {len(content)} bytes)"
        )

        # Start async processing without await (fire-and-forget)
        asyncio.create_task(process_audio_file(audio_file_path, visit_id))

        return JSONResponse(content={"status": "queued"}, status_code=202)

    except Exception as e:
        logger.error(f"Visit {visit_id}: Error uploading audio file - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


async def get_visit_status(visit_id: str):
    """
    Optional endpoint to check the status of a visit.
    """
    if visit_id not in visits_store:
        raise HTTPException(status_code=404, detail="Visit not found")

    return JSONResponse(content=visits_store[visit_id])


async def list_visits():
    """
    Optional endpoint to list all visits.
    """
    return JSONResponse(content={"visits": list(visits_store.values())})
