from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import zipfile
import os
import shutil
import uuid

from app.database import engine, get_db
from app.chunker import extract_java_chunks
from app import models

from app.embeddings import generate_embedding
from app.vector_store import (
    create_index,
    add_embedding,
    save_index,
    load_index,
    search
)

from app.llm_service import generate_response

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
TEMP_DIR = "temp"
SIMILARITY_THRESHOLD = 0.45


# ============================
# Root
# ============================

@app.get("/")
def root():
    return {"message": "AI Codebase Intelligence System 🚀 (Phase 7)"}


# ============================
# Upload Repository
# ============================

@app.post("/upload-repository")
def upload_repository(file: UploadFile = File(...), db: Session = Depends(get_db)):

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files allowed")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    zip_path = os.path.join(TEMP_DIR, unique_name)

    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    temp_extract_path = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    os.makedirs(temp_extract_path, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_extract_path)
    except zipfile.BadZipFile:
        os.remove(zip_path)
        shutil.rmtree(temp_extract_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail="Invalid zip file")

    repo = models.Repository(name=file.filename)
    db.add(repo)
    db.commit()
    db.refresh(repo)

    repo_path = os.path.join(UPLOAD_DIR, str(repo.id))
    shutil.move(temp_extract_path, repo_path)

    for root_dir, dirs, files in os.walk(repo_path):

        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "target", "__pycache__"]]

        for filename in files:

            if filename.endswith(".java"):

                full_path = os.path.join(root_dir, filename)
                relative_path = os.path.relpath(full_path, repo_path)
                file_size = os.path.getsize(full_path)

                db_file = models.File(
                    file_path=relative_path,
                    language="Java",
                    size=file_size,
                    repo_id=repo.id
                )

                db.add(db_file)
                db.commit()
                db.refresh(db_file)

                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                chunks = extract_java_chunks(content)

                for chunk in chunks:

                    db_chunk = models.CodeChunk(
                        content=chunk["content"],
                        class_name=chunk["class_name"],
                        method_name=chunk["method_name"],
                        start_line=chunk["start_line"],
                        end_line=chunk["end_line"],
                        file_id=db_file.id
                    )

                    db.add(db_chunk)

    db.commit()
    os.remove(zip_path)

    return {
        "message": "Repository uploaded successfully",
        "repository_id": repo.id
    }


# ============================
# Build FAISS Index
# ============================

@app.post("/build-index")
def build_index(db: Session = Depends(get_db)):

    chunks = db.query(models.CodeChunk).all()

    if not chunks:
        return {"message": "No chunks found"}

    create_index()

    for chunk in chunks:
        embedding = generate_embedding(chunk.content)
        add_embedding(embedding, chunk.id)

    save_index()

    return {
        "message": "FAISS index built",
        "chunks_indexed": len(chunks)
    }


# ==================================
# Semantic Search
# ==================================

@app.post("/search")
def search_code(query: str, db: Session = Depends(get_db)):

    load_index()

    query_embedding = generate_embedding(query)

    search_results = search(query_embedding, top_k=5)

    filtered_results = [
        item for item in search_results
        if item["score"] >= SIMILARITY_THRESHOLD
    ]

    if not filtered_results:
        return {"message": "No sufficiently relevant code found"}

    score_map = {item["chunk_id"]: item["score"] for item in filtered_results}

    chunks = db.query(models.CodeChunk).filter(
        models.CodeChunk.id.in_(score_map.keys())
    ).all()

    chunks.sort(key=lambda c: score_map.get(c.id, 0), reverse=True)

    results = []

    for chunk in chunks:

        results.append({
            "chunk_id": chunk.id,
            "class_name": chunk.class_name,
            "method_name": chunk.method_name,
            "similarity_score": round(score_map.get(chunk.id, 0), 4),
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "content": chunk.content[:500]
        })

    return {"results": results}


# ============================
# Request Models
# ============================

class RAGRequest(BaseModel):
    query: str
    repo_id: int
    mode: str = "strict"


class RepoAnalysisRequest(BaseModel):
    repo_id: int


# ============================
# Prompt Builders
# ============================

def build_prompt(query, chunks, mode):

    context = "\n\n".join(
        [
            f"Class: {c.class_name}\nMethod: {c.method_name}\nCode:\n{c.content}"
            for c in chunks
        ]
    )

    if mode == "strict":

        system_instruction = (
            "You are a code analysis assistant.\n"
            "Explain the answer using only information visible in the provided code context.\n"
            "Describe the relevant method behavior clearly.\n"
            "Do NOT assume UI behavior or missing system logic.\n"
            "If the answer is not visible, respond exactly with:\n"
            "'The answer is not found in the provided code.'"
        )

    else:

        system_instruction = (
            "You are a helpful code assistant.\n"
            "Explain clearly what the provided code does.\n"
            "Only describe behavior that is explicitly visible in the code."
        )

    return f"""
{system_instruction}

Context:
{context}

Question:
{query}

Answer:
"""


def build_repo_analysis_prompt(chunks):

    context = "\n\n".join(
        [
            f"Class: {c.class_name}\nMethod: {c.method_name}\nCode:\n{c.content[:800]}"
            for c in chunks
        ]
    )

    return f"""
You are a senior software engineer analyzing a codebase.

Explain the architecture of the repository using ONLY information visible in the provided code.

Rules:
- Only describe classes and behaviors visible in the code
- Do NOT assume frameworks, logging systems, or design patterns
- Do NOT invent components that are not present
- If a component's role is unclear, say "its purpose is not fully visible in the provided code"

Focus on:
- Main classes
- Their responsibilities
- How they interact

Code context:
{context}

Architecture explanation:
"""


# ============================
# RAG Query
# ============================

@app.post("/rag-query")
def rag_query(request: RAGRequest, db: Session = Depends(get_db)):

    load_index()

    query_embedding = generate_embedding(request.query)

    search_results = search(query_embedding, top_k=4)

    filtered_results = [
        item for item in search_results
        if item["score"] >= SIMILARITY_THRESHOLD
    ]

    if not filtered_results:
        return {"message": "No sufficiently relevant code found"}

    chunk_score_map = {item["chunk_id"]: item["score"] for item in filtered_results}

    chunks = (
        db.query(models.CodeChunk)
        .join(models.File)
        .filter(
            models.CodeChunk.id.in_(chunk_score_map.keys()),
            models.File.repo_id == request.repo_id
        )
        .all()
    )

    chunks.sort(key=lambda c: chunk_score_map.get(c.id, 0), reverse=True)

    if not chunks:
        return {"message": "No relevant chunks found in this repository"}

    prompt = build_prompt(request.query, chunks, request.mode)

    llm_response = generate_response(prompt)

    return {
        "mode": request.mode,
        "retrieved_chunks": [
            {"chunk_id": c.id, "class": c.class_name, "method": c.method_name}
            for c in chunks
        ],
        "answer": llm_response
    }


# =================================
# Repository Architecture Analysis
# =================================

@app.post("/analyze-repository")
def analyze_repository(request: RepoAnalysisRequest, db: Session = Depends(get_db)):

    repo = db.query(models.Repository).filter(
        models.Repository.id == request.repo_id
    ).first()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    chunks = (
        db.query(models.CodeChunk)
        .join(models.File)
        .filter(models.File.repo_id == request.repo_id)
        .order_by(models.CodeChunk.class_name)
        .all()
    )

    class_chunks = {}

    for chunk in chunks:
        if chunk.class_name not in class_chunks:
            class_chunks[chunk.class_name] = chunk

    representative_chunks = list(class_chunks.values())[:10]

    if not chunks:
        return {"message": "No code found in repository"}

    prompt = build_repo_analysis_prompt(representative_chunks)

    response = generate_response(prompt)

    return {
        "repository_id": request.repo_id,
        "analysis": response
    }