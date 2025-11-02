"""SOAP note generation service."""

import asyncio
from configs.prompts import (
    SOAP_SUBJECTIVE_PROMPT,
    SOAP_OBJECTIVE_PROMPT,
    SOAP_ASSESSMENT_PROMPT,
    SOAP_PLAN_PROMPT,
)
from configs.settings import SOAP_SECTION_MAX_TOKENS
from helpers.soap_formatter import clean_soap_formatting
from services.llm_service import generate_chat_response_sync
from utils.logger import logger
from utils.storage import visits_store


async def generate_soap_section(
    transcript: str, section_prompt: str, section_name: str, visit_id: str
) -> str:
    """
    Generate a single SOAP section using the Mistral model.

    Args:
        transcript: The conversation transcript
        section_prompt: The system prompt for this section
        section_name: Name of the section (Subjective, Objective, Assessment, Plan)
        visit_id: Visit ID for tracking

    Returns:
        str: Generated SOAP section content

    Raises:
        Exception: If section generation fails
    """
    try:
        logger.info(f"Visit {visit_id}: Starting {section_name} section generation")

        # Prepare the messages for this specific section
        messages = [
            {"role": "system", "content": section_prompt},
            {
                "role": "user",
                "content": f"Here is the verbatim transcript of the doctor-patient encounter:\n\n{transcript}",
            },
        ]

        # Run generation in executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()

        # Use more conservative parameters for SOAP sections
        section_content = await loop.run_in_executor(
            None,
            lambda: generate_chat_response_sync(
                messages, max_new_tokens=SOAP_SECTION_MAX_TOKENS, section_mode=True
            ),
        )

        # Clean up common formatting issues
        section_content = clean_soap_formatting(section_content, section_name)

        logger.info(
            f"Visit {visit_id}: {section_name} section generation completed. Length: {len(section_content)} characters"
        )

        return section_content.strip()

    except Exception as e:
        logger.error(
            f"Visit {visit_id}: {section_name} section generation failed - {str(e)}"
        )
        raise Exception(f"{section_name} section generation failed: {str(e)}")


async def generate_soap_note(transcript: str, visit_id: str) -> str:
    """
    Generate SOAP note using agentic approach - section by section.

    Args:
        transcript: The conversation transcript
        visit_id: Visit ID for tracking

    Returns:
        str: Complete SOAP note

    Raises:
        Exception: If SOAP note generation fails
    """
    try:
        visits_store[visit_id]["status"] = "generating_soap"
        visits_store[visit_id]["progress"] = 50
        logger.info(
            f"Visit {visit_id}: Starting agentic SOAP note generation with transcript length: {len(transcript)} characters"
        )

        # Define the sections and their prompts
        sections = [
            ("Subjective", SOAP_SUBJECTIVE_PROMPT),
            ("Objective", SOAP_OBJECTIVE_PROMPT),
            ("Assessment", SOAP_ASSESSMENT_PROMPT),
            ("Plan", SOAP_PLAN_PROMPT),
        ]

        soap_sections = []

        for i, (section_name, section_prompt) in enumerate(sections):
            # Update progress tracking
            visits_store[visit_id]["current_section"] = section_name
            section_progress = 50 + int((i / len(sections)) * 40)
            visits_store[visit_id]["progress"] = section_progress

            logger.info(
                f"Visit {visit_id}: Generating {section_name} section ({i + 1}/{len(sections)}) - Progress: {section_progress}%"
            )

            # Generate this section
            section_content = await generate_soap_section(
                transcript, section_prompt, section_name, visit_id
            )
            soap_sections.append(section_content)

        # Combine all sections
        full_soap_note = "\n\n".join(soap_sections)

        # Clean up progress tracking fields
        if "current_section" in visits_store[visit_id]:
            del visits_store[visit_id]["current_section"]

        visits_store[visit_id]["progress"] = 90
        logger.info(
            f"Visit {visit_id}: Agentic SOAP note generation completed. Total length: {len(full_soap_note)} characters"
        )

        return full_soap_note.strip()

    except Exception as e:
        # Clean up progress tracking fields on error
        if "current_section" in visits_store[visit_id]:
            del visits_store[visit_id]["current_section"]

        logger.error(
            f"Visit {visit_id}: Agentic SOAP note generation failed - {str(e)}"
        )
        raise Exception(f"SOAP note generation failed: {str(e)}")
