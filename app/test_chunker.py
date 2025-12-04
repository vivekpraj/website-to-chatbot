from app.services.text_processing import process_text_to_chunks

text = """
This is a test. This is another sentence! Here is more content?
And here is a very long paragraph that should be chunked correctly.
"""

chunks = process_text_to_chunks(text)

print(f"Total chunks = {len(chunks)}\n")
for c in chunks:
    print("----- CHUNK -----")
    print(c)
