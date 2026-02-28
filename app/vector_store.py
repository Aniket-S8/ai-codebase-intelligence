import faiss
import numpy as np
import os
import pickle

INDEX_PATH = "faiss_index"
INDEX_FILE = os.path.join(INDEX_PATH, "code_index.faiss")
MAPPING_FILE = os.path.join(INDEX_PATH, "id_mapping.pkl")

dimension = 384  # matches all-MiniLM-L6-v2

# Use Inner Product for cosine similarity
index = faiss.IndexFlatIP(dimension)

id_mapping = []


def normalize(vector: np.ndarray):
    return vector / np.linalg.norm(vector)


def create_index():
    global index, id_mapping
    index = faiss.IndexFlatIP(dimension)
    id_mapping = []


def add_embedding(embedding: np.ndarray, chunk_id: int):
    global index, id_mapping
    normalized_embedding = normalize(embedding)
    index.add(np.array([normalized_embedding]))
    id_mapping.append(chunk_id)


def save_index():
    os.makedirs(INDEX_PATH, exist_ok=True)
    faiss.write_index(index, INDEX_FILE)
    with open(MAPPING_FILE, "wb") as f:
        pickle.dump(id_mapping, f)


def load_index():
    global index, id_mapping
    if os.path.exists(INDEX_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(MAPPING_FILE, "rb") as f:
            id_mapping = pickle.load(f)


def search(query_embedding, top_k=5):
    normalized_query = normalize(query_embedding)
    
    similarities, indices = index.search(
        np.array([normalized_query]), top_k
    )

    results = []

    for position, idx in enumerate(indices[0]):
        if idx < len(id_mapping):
            results.append({
                "chunk_id": id_mapping[idx],
                "score": float(similarities[0][position])
            })

    return results