"""Progress streaming controller for SSE."""

import json
import asyncio
from typing import AsyncGenerator
from fastapi import HTTPException
from starlette.responses import StreamingResponse
from utils.storage import visits_store
from utils.logger import logger


async def get_progress_stream(visit_id: str):
    """
    SSE endpoint to stream real-time progress updates for a visit.
    """
    if visit_id not in visits_store:
        logger.warning(
            f"Visit {visit_id}: Progress stream requested for non-existent visit"
        )
        raise HTTPException(status_code=404, detail="Visit not found")

    logger.info(f"Visit {visit_id}: Starting SSE progress stream")

    async def event_stream() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events for progress updates"""
        last_status = None
        last_progress = None
        last_chunk = None
        last_chunk_status = None
        last_section = None

        # Send initial update immediately when stream starts
        if visit_id in visits_store:
            visit_data = visits_store[visit_id]
            initial_status = visit_data.get("status")
            initial_progress = visit_data.get("progress", 0)

            initial_event_data = {
                "visit_id": visit_id,
                "status": initial_status,
                "progress": initial_progress,
                "timestamp": asyncio.get_event_loop().time(),
            }

            # Add chunk information if available (during transcription)
            if visit_data.get("current_chunk") is not None:
                initial_event_data["current_chunk"] = visit_data.get("current_chunk")
                initial_event_data["total_chunks"] = visit_data.get("total_chunks")
                initial_event_data["chunk_status"] = visit_data.get("chunk_status")

            # Add section information if available (during SOAP generation)
            if visit_data.get("current_section") is not None:
                initial_event_data["current_section"] = visit_data.get(
                    "current_section"
                )

            if initial_status == "completed":
                initial_event_data["soap_note"] = visit_data.get("soap_note")
            elif initial_status == "error":
                initial_event_data["error"] = visit_data.get("error")

            yield f"data: {json.dumps(initial_event_data)}\n\n"
            logger.info(
                f"Visit {visit_id}: SSE initial update sent - Status: {initial_status}, Progress: {initial_progress}%"
            )

            last_status = initial_status
            last_progress = initial_progress
            last_chunk = visit_data.get("current_chunk")
            last_chunk_status = visit_data.get("chunk_status")
            last_section = visit_data.get("current_section")

        while True:
            if visit_id not in visits_store:
                break

            visit_data = visits_store[visit_id]
            current_status = visit_data.get("status")
            current_progress = visit_data.get("progress", 0)

            # Check if chunk processing info has changed
            current_chunk = visit_data.get("current_chunk")
            current_chunk_status = visit_data.get("chunk_status")
            chunk_changed = (
                current_chunk != last_chunk or current_chunk_status != last_chunk_status
            )

            # Check if section processing info has changed
            current_section = visit_data.get("current_section")
            section_changed = current_section != last_section

            # Only trigger update for chunk changes if we currently have chunk info
            valid_chunk_change = chunk_changed and (
                current_chunk is not None or last_chunk is not None
            )

            if (
                current_status != last_status
                or current_progress != last_progress
                or valid_chunk_change
                or section_changed
            ):
                event_data = {
                    "visit_id": visit_id,
                    "status": current_status,
                    "progress": current_progress,
                    "timestamp": asyncio.get_event_loop().time(),
                }

                # Add chunk processing information only if currently available
                if (
                    visit_data.get("current_chunk") is not None
                    and visit_data.get("total_chunks") is not None
                    and visit_data.get("chunk_status") is not None
                ):
                    event_data["current_chunk"] = visit_data.get("current_chunk")
                    event_data["total_chunks"] = visit_data.get("total_chunks")
                    event_data["chunk_status"] = visit_data.get("chunk_status")

                # Add section processing information if available
                if visit_data.get("current_section") is not None:
                    event_data["current_section"] = visit_data.get("current_section")

                # Add additional data based on status
                if current_status == "completed":
                    event_data["soap_note"] = visit_data.get("soap_note")
                    event_data["transcript"] = visit_data.get("transcript")
                    event_data["generation_time"] = visit_data.get("generation_time")
                    event_data["audio_duration"] = visit_data.get("audio_duration")
                    event_data["transcription_time"] = visit_data.get(
                        "transcription_time"
                    )
                elif current_status == "error":
                    event_data["error"] = visit_data.get("error")

                yield f"data: {json.dumps(event_data)}\n\n"

                # Log progress updates
                chunk_info = ""
                if current_chunk is not None:
                    chunk_info = f", Chunk: {current_chunk}/{visit_data.get('total_chunks', '?')}"

                section_info = ""
                if current_section is not None:
                    section_info = f", Section: {current_section}"

                logger.info(
                    f"Visit {visit_id}: SSE update sent - Status: {current_status}, Progress: {current_progress}%{chunk_info}{section_info}"
                )

                last_status = current_status
                last_progress = current_progress
                last_chunk = current_chunk
                last_chunk_status = current_chunk_status
                last_section = current_section

                # Break the loop if processing is complete or failed
                if current_status in ["completed", "error"]:
                    logger.info(
                        f"Visit {visit_id}: SSE stream ending - Final status: {current_status}"
                    )
                    break

            # Wait before next check - shorter interval for better responsiveness
            await asyncio.sleep(0.2)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )
