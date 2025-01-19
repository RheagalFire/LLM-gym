import tiktoken
from typing import Optional


def chunk_text_with_overlap(
    text: str, max_tokens: Optional[int] = None, overlap: Optional[int] = None
) -> list[str]:
    """
    Splits the input text into overlapping chunks based on token count.

    Args:
        text (str): The text to be chunked.
        max_tokens (int): The maximum number of tokens per chunk.
        overlap (int): The number of overlapping tokens between chunks.

    Returns:
        list[str]: A list of text chunks.
    """
    if max_tokens is None:
        max_tokens = 1000
    if overlap is None:
        overlap = 100
    encoding = tiktoken.get_encoding("cl100k_base")  # Specify the encoding model
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        if end >= len(tokens):
            break
        # Move back by 'overlap' tokens for the next chunk
        start = end - overlap
    return chunks


if __name__ == "__main__":
    sample_text = (
        "This is a sample text to be chunked. It contains various words and phrases to test the chunking process. The text is designed to be long enough to demonstrate the effectiveness of the chunking algorithm."
        * 1
    )
    chunks = chunk_text_with_overlap(sample_text)
    print(len(chunks))
