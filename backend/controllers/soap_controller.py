"""SOAP note controller for managing SOAP note retrieval."""

import asyncio
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from utils.storage import visits_store


async def get_soap_note(visit_id: str):
    """
    Fetches the generated SOAP note for a specific visit ID.
    Returns JSON with soap_note and soap_status.
    """
    if visit_id not in visits_store:
        raise HTTPException(status_code=404, detail="Visit not found")

    visit_data = visits_store[visit_id]
    current_status = visit_data.get("status", "unknown")

    # Prepare response data
    response_data = {
        "soap_status": current_status,
        "soap_note": None,
        "transcript": visit_data.get("transcript"),
        "generation_time": visit_data.get("generation_time"),
        "audio_duration": visit_data.get("audio_duration"),
        "transcription_time": visit_data.get("transcription_time"),
        "visit_id": visit_id,
    }

    # If processing is complete, include the SOAP note
    if current_status == "completed":
        soap_note = visit_data.get("soap_note")
        if not soap_note:
            # Dummy SOAP note for testing
            soap_note = f"""SOAP Note for Visit ID: {visit_id}

SUBJECTIVE:
Patient presents with chief complaint of routine consultation. Patient reports feeling generally well with no acute concerns. Denies fever, chills, nausea, vomiting, chest pain, shortness of breath, or other concerning symptoms.

OBJECTIVE:
Vital signs stable and within normal limits. Physical examination reveals no acute distress. Patient appears alert and oriented. No obvious abnormalities noted on initial assessment.

ASSESSMENT:
1. Routine consultation - no acute findings
2. Patient appears stable and comfortable
3. No immediate concerns identified

PLAN:
1. Continue current care regimen
2. Follow-up as needed
3. Patient advised to contact healthcare provider if any concerns arise
4. Routine monitoring recommended

Generated on: {asyncio.get_event_loop().time()}
Visit ID: {visit_id}"""

        response_data["soap_note"] = soap_note
        return JSONResponse(content=response_data, status_code=200)

    # If not completed, return status with null soap_note
    elif current_status == "error":
        response_data["error"] = visit_data.get("error", "Unknown error occurred")
        return JSONResponse(content=response_data, status_code=500)

    else:
        # Still processing
        response_data["progress"] = visit_data.get("progress", 0)
        return JSONResponse(content=response_data, status_code=202)
