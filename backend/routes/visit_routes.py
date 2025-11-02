"""Visit-related routes."""

from fastapi import APIRouter, File, UploadFile
from controllers.visit_controller import (
    create_visit,
    process_soap_note,
    get_visit_status,
    list_visits,
)

router = APIRouter()


@router.post("/visit")
async def create_visit_route():
    """Create a new visit."""
    return await create_visit()


@router.post("/soap/{visit_id}")
async def process_soap_note_route(visit_id: str, audio_file: UploadFile = File(...)):
    """Process SOAP note for a visit."""
    return await process_soap_note(visit_id, audio_file)


@router.get("/visit/{visit_id}")
async def get_visit_status_route(visit_id: str):
    """Get visit status."""
    return await get_visit_status(visit_id)


@router.get("/visits")
async def list_visits_route():
    """List all visits."""
    return await list_visits()
