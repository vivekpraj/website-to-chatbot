from app.services.embeddings import embed_text

chunks = [
    "This is chunk one.",
    "This is chunk two."
]

vecs = embed_text(chunks)

print(vecs.shape)   # Expect (2, 384)
