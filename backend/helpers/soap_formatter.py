"""SOAP note formatting utilities."""

import re


def clean_soap_formatting(content: str, section_name: str) -> str:
    """
    Clean up common formatting issues in SOAP sections.

    Args:
        content: The SOAP section content to clean
        section_name: Name of the section (subjective, objective, assessment, plan)

    Returns:
        str: Cleaned contesnt
    """
    # Remove trailing backslashes and fix common formatting issues
    content = re.sub(r"\\+$", "", content)  # Remove trailing backslashes
    content = re.sub(r"\\+\s*\n", "\n", content)  # Remove backslashes at end of lines
    content = re.sub(r":\\\s*\n", ":\n", content)  # Fix ":\\" patterns
    content = re.sub(
        r"#\s*([A-Za-z]+):\\\s*", r"# \1:\n", content
    )  # Fix section headers with backslashes

    # Fix numbering issues in Assessment section
    if section_name.lower() == "assessment":
        # Fix malformed numbering like "1.\*" or "1.*"
        content = re.sub(r"(\d+)\.\\\*\s*", r"\1. ", content)
        content = re.sub(r"(\d+)\.\*\s*", r"\1. ", content)
        content = re.sub(r"(\d+)\\\.\s*", r"\1. ", content)

        # Fix ICD-10 code formatting issues
        content = re.sub(r"ICDS-11:", "ICD-10:", content)
        content = re.sub(r"ICDC-1o:", "ICD-10:", content)
        content = re.sub(r"ICD-1O:", "ICD-10:", content)  # Fix O instead of 0

    # Fix Plan section formatting
    if section_name.lower() == "plan":
        # Fix bullet point inconsistencies
        content = re.sub(r"^\s*\*\s*", "- ", content, flags=re.MULTILINE)
        content = re.sub(r"^\s*\+\s*", "  - ", content, flags=re.MULTILINE)

        # Fix section headers
        content = re.sub(r"^###\s*", "## ", content, flags=re.MULTILINE)
        content = re.sub(r"^####\s*", "### ", content, flags=re.MULTILINE)

    # Fix Objective section formatting
    if section_name.lower() == "objective":
        # Ensure proper bullet point format
        content = re.sub(r"^-\s*([A-Za-z])", r"- \1", content, flags=re.MULTILINE)

    # Fix Subjective section formatting
    if section_name.lower() == "subjective":
        # Remove unwanted explanatory notes and disclaimers
        content = re.sub(
            r"\(Note:.*?based on.*?\.\)\s*",
            "",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        content = re.sub(
            r"\(This summary is based on.*?\.\)\s*",
            "",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        content = re.sub(
            r"\(Based on.*?information.*?\.\)\s*",
            "",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Ensure header and content are on separate lines
        content = re.sub(
            r"^#\s*Subjective:\s*(.+)",
            r"# Subjective:\n\1",
            content,
            flags=re.MULTILINE,
        )
        # Also handle cases where there's no space after the colon
        content = re.sub(
            r"^#\s*Subjective:([^\n])",
            r"# Subjective:\n\1",
            content,
            flags=re.MULTILINE,
        )

    # General cleanup
    content = re.sub(r"\s+\n", "\n", content)  # Remove trailing whitespace
    content = re.sub(r"\n{3,}", "\n\n", content)  # Reduce multiple newlines
    content = content.strip()

    return content
