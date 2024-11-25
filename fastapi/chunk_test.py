from transformers import GPT2Tokenizer
import json

# Initialize a tokenizer (You can replace this with the Llama3 tokenizer when available)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def chunk_content(content, chunk_size=512, overlap=50):
    """
    Splits text content into fixed-length chunks with overlap.

    Parameters:
    - content: str, the text to be chunked.
    - chunk_size: int, maximum number of tokens per chunk.
    - overlap: int, number of tokens to overlap between chunks.

    Returns:
    - List of text chunks.
    """
    tokens = tokenizer.tokenize(content)
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(tokenizer.convert_tokens_to_string(chunk))

    return chunks

# Example usage
data = json.load(open('syllabi.json','r'))

# Chunk each page's content and store it
chunked_data = []
highest_chunk_number=0
for entry in data:
    if not entry["content"]:
        entry["content"] = ""
    chunks = chunk_content(entry["content"], chunk_size=512, overlap=50)
    for idx, chunk in enumerate(chunks):
        chunked_data.append({
            "filename": entry["filename"],
            "chunk_number": idx + 1,
            "content": chunk
        })
        highest_chunk_number=max(highest_chunk_number,idx+1)

# Output: View chunked data
print(json.dumps(chunked_data,indent=2))
print(f"HIGHEST CHUNK NUMBER: {highest_chunk_number}")