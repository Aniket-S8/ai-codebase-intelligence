# 🧠 AI Codebase Intelligence System

An AI-powered developer tool that enables semantic search, architecture analysis, and intelligent reasoning over software codebases using a custom Retrieval-Augmented Generation (RAG) pipeline.

---

# 🚀 Overview

AI Codebase Intelligence System is designed to help developers:

- Understand large codebases quickly  
- Perform semantic search across files  
- Analyze architecture  
- Detect potential security risks  
- Generate intelligent explanations of code  

This system is built from scratch without orchestration frameworks (e.g., LangChain) to demonstrate deep understanding of embeddings, vector search, and RAG architecture.

---

# 🏗 Architecture

- User Query
- ↓
- Embedding Model (Local)
- ↓
- FAISS Vector Search
- ↓
- Retrieve Relevant Code Chunks
- ↓
- Local LLM (Ollama)
- ↓
- Structured AI Response

---

# 🧱 Tech Stack

## Backend

- FastAPI  
- SQLAlchemy  
- PostgreSQL (Docker)  
- Uvicorn  

## AI / RAG

- Sentence Transformers (local embeddings)  
- FAISS (vector search)  
- Local LLM via Ollama  
- Custom prompt engineering  

## DevOps

- Docker  
- VS Code  
- Git & GitHub  

