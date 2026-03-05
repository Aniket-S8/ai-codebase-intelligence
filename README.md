# 🧠 AI Codebase Intelligence System

An **AI-powered developer tool** that enables semantic search,
architecture analysis, and intelligent reasoning over software codebases
using a custom **Retrieval-Augmented Generation (RAG)** pipeline.

This system helps developers quickly understand unfamiliar repositories
by combining **code embeddings, vector search, and local LLM
reasoning**.

------------------------------------------------------------------------

# 🚀 Overview

Understanding large codebases is one of the biggest challenges
developers face.\
This project provides an **AI-assisted interface for exploring and
analyzing repositories**.

The system can:

-   Perform **semantic search across code**
-   Explain **how specific functionality works**
-   Identify **classes and methods responsible for behavior**
-   Provide **architecture-level summaries of repositories**
-   Return **source citations for retrieved code**

Unlike many GenAI projects, this system is built **from scratch without
orchestration frameworks like LangChain**, demonstrating a deeper
understanding of the underlying architecture of RAG systems.

------------------------------------------------------------------------

# 🏗 System Architecture

    Repository ZIP Upload
            ↓
    Code Extraction & Java Parsing
            ↓
    Code Chunking
            ↓
    Embedding Generation (Sentence Transformers)
            ↓
    FAISS Vector Index
            ↓
    Semantic Retrieval
            ↓
    Prompt Construction
            ↓
    Local LLM (Ollama)
            ↓
    AI Code Explanation / Architecture Analysis

------------------------------------------------------------------------

# ⚙️ Tech Stack

## Backend

-   FastAPI -- API framework
-   SQLAlchemy -- ORM for database interaction
-   PostgreSQL (Docker) -- metadata storage
-   Uvicorn -- ASGI server

## AI / RAG

-   Sentence Transformers
-   FAISS Vector Search
-   Cosine Similarity Retrieval
-   Prompt Engineering
-   Local LLM via Ollama

## Development Tools

-   Python
-   Docker
-   VS Code
-   Git & GitHub

------------------------------------------------------------------------

# 🧩 Key Features

## 📦 Repository Ingestion

Upload a repository as a `.zip` file.

The system automatically:

-   extracts Java source files
-   parses classes and methods
-   stores metadata in PostgreSQL
-   creates structured code chunks

------------------------------------------------------------------------

## 🔎 Semantic Code Search

Developers can ask natural language queries such as:

-   How does the system add a new task?
-   Which class marks a task as completed?

The system:

1.  converts the query to embeddings
2.  performs vector similarity search
3.  retrieves relevant code chunks
4.  returns structured results with similarity scores

Example response:

    Class: AddTask
    Method: executeAction
    Similarity Score: 0.62
    Lines: 83–91

------------------------------------------------------------------------

## 🤖 AI Code Explanation (RAG)

Using retrieved code context, the system generates explanations using a
local LLM.

Two reasoning modes are supported:

### Strict Mode

-   grounded strictly in retrieved code
-   avoids speculation
-   useful for accurate code understanding

### Assistant Mode

-   more conversational explanation
-   easier for learning unfamiliar code

------------------------------------------------------------------------

## 🏛 Repository Architecture Analysis

The system can analyze a repository and explain its architecture.

Example query:

    Analyze the architecture of this repository

The system identifies:

-   main classes
-   their responsibilities
-   interactions between components

This is achieved using **class-based code sampling** rather than random
chunk selection.

------------------------------------------------------------------------

## 📌 Source Citations

AI responses include references to the original code.

Example:

    Sources:
    - AddTask.executeAction (lines 83–91)
    - AddTask.showActionsInformation (lines 25–31)

This improves **trust and traceability** of AI-generated explanations.

------------------------------------------------------------------------

# 📡 API Endpoints

## Upload Repository

    POST /upload-repository

Upload a `.zip` file containing a repository.

------------------------------------------------------------------------

## Build Vector Index

    POST /build-index

Generates embeddings and builds the FAISS index.

------------------------------------------------------------------------

## Semantic Search

    POST /search

Example:

    query = "How does a task get added?"

Returns the most relevant code chunks.

------------------------------------------------------------------------

## RAG Code Query

    POST /rag-query

Example request:

``` json
{
  "query": "How is a new task added?",
  "repo_id": 1,
  "mode": "strict"
}
```

------------------------------------------------------------------------

## Repository Architecture Analysis

    POST /analyze-repository

Example request:

``` json
{
  "repo_id": 1
}
```

Returns an AI-generated explanation of the repository structure.

------------------------------------------------------------------------

# 🧪 Example Queries

-   How does the TodoList add a new task?
-   Which class marks a task as completed?
-   Explain the repository architecture
-   Where are tasks stored in the system?

------------------------------------------------------------------------

# 🧠 Design Principles

This project focuses on **understanding and implementing core GenAI
infrastructure manually**.

Key principles:

-   No orchestration frameworks (LangChain intentionally avoided)
-   Fully local AI stack
-   Transparent RAG pipeline
-   Modular backend architecture
-   Reproducible development environment

------------------------------------------------------------------------

# 📊 Why This Project Matters

Most AI projects only demonstrate basic prompt usage.

This system demonstrates real-world AI engineering concepts:

-   vector databases
-   semantic retrieval
-   prompt engineering
-   LLM grounding
-   developer tooling

It resembles the architecture used in modern tools such as:

-   GitHub Copilot Chat (codebase mode)
-   Sourcegraph Cody
-   Cursor AI code search systems

------------------------------------------------------------------------

# 📦 Local Setup

### Clone repository

    git clone <repo_url>
    cd ai-codebase-intelligence

### Create virtual environment

    python -m venv venv
    venv\Scripts\activate

### Install dependencies

    pip install -r requirements.txt

### Start PostgreSQL (Docker)

    docker start ai-postgres

### Run the API

    uvicorn app.main:app --reload

Swagger UI:

    http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# 📈 Future Improvements

Possible future extensions:

- 