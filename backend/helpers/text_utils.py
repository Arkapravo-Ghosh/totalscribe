"""Text processing utilities."""


def remove_overlap(prev_text: str, curr_text: str, max_overlap_chars: int = 80) -> str:
    """
    Remove overlapping text between consecutive transcription chunks.

    Args:
        prev_text: Previous text chunk
        curr_text: Current text chunk
        max_overlap_chars: Maximum number of characters to check for overlap

    Returns:
        str: Current text with overlap removed
    """
    max_overlap_chars = min(max_overlap_chars, len(prev_text), len(curr_text))
    for i in range(max_overlap_chars, 0, -1):
        if prev_text[-i:] == curr_text[:i]:
            return curr_text[i:]
    return curr_text
