from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import zipfile
import os
import shutil
import uuid

from app.database import engine, get_db
from app.chunker import extract_java_chunks
from app import models

from app.embeddings import generate_embedding
from app.vector_store import create_index, add_embedding, save_index, load_index, search

app = FastAPI()

# Create DB tables
models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
TEMP_DIR = "temp"

@app.get("/")
def root():
    return {"message": "Phase 2 started 🚀"}


@app.post("/upload-repository")
def upload_repository(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    # Ensure directories exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Unique filename to prevent collision
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    zip_path = os.path.join(TEMP_DIR, unique_name)

    # Save uploaded file temporarily
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Attempt extraction into temp folder
    temp_extract_path = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    os.makedirs(temp_extract_path, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_extract_path)
    except zipfile.BadZipFile:
        os.remove(zip_path)
        shutil.rmtree(temp_extract_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail="Invalid zip file")

    # Create repository entry ONLY after successful extraction
    repo = models.Repository(name=file.filename)
    db.add(repo)
    db.commit()
    db.refresh(repo)

    # Final repository storage path
    repo_path = os.path.join(UPLOAD_DIR, str(repo.id))
    shutil.move(temp_extract_path, repo_path)

    # Scan and register Java files
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "target", "__pycache__"]]

        for filename in files:
            if filename.endswith(".java"):
                full_path = os.path.join(root, filename)
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

                # Read file content
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

    return {"message": "FAISS index built", "chunks_indexed": len(chunks)}

@app.post("/search")
def search_code(query: str, db: Session = Depends(get_db)):
    load_index()

    query_embedding = generate_embedding(query)

    search_results = search(query_embedding, top_k=5)

    if not search_results:
        return {"message": "No relevant chunks found"}

    chunk_ids = [item["chunk_id"] for item in search_results]

    chunks = db.query(models.CodeChunk).filter(
        models.CodeChunk.id.in_(chunk_ids)
    ).all()

    # Map chunk_id to score
    score_map = {item["chunk_id"]: item["score"] for item in search_results}

    results = []

    for chunk in chunks:
        results.append({
            "chunk_id": chunk.id,
            "class_name": chunk.class_name,
            "method_name": chunk.method_name,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "similarity_score": round(score_map.get(chunk.id, 0), 4),
            "content": chunk.content[:500]
        })

    return {"results": results}

    # Cleanup
    os.remove(zip_path)

    return {
        "message": "Repository uploaded successfully",
        "repository_id": repo.id
    }