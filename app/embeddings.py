from sentence_transformers import SentenceTransformer
import numpy as np

# Lightweight and strong model
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    """
    Generate embedding for given text.
    Returns numpy array.
    """
    embedding = model.encode(text)
    return np.array(embedding, dtype=np.float32)