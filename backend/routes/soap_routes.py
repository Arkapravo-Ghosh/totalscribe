"""SOAP note and progress-related routes."""

from fastapi import APIRouter
from controllers.soap_controller import get_soap_note
from controllers.progress_controller import get_progress_stream

router = APIRouter()


@router.get("/soap/{visit_id}")
async def get_soap_note_route(visit_id: str):
    """Get SOAP note for a visit."""
    return await get_soap_note(visit_id)


@router.get("/progress/{visit_id}")
async def get_progress_stream_route(visit_id: str):
    """Get real-time progress stream for a visit."""
    return await get_progress_stream(visit_id)
