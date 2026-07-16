# Enterprise AI Knowledge Assistant

A production-grade RAG (Retrieval-Augmented Generation) platform allowing
employees to upload company documents and query them via AI — with
mandatory source citations, multi-tenant isolation, and enterprise features
like RBAC, analytics, and feedback tracking.

Built over 60 days as a portfolio project demonstrating backend engineering,
AI engineering, and full-stack system design.

## Features

- 🔐 JWT auth with role-based access control (viewer/editor/admin)
- 📄 Multi-format document ingestion: PDF, DOCX, PPTX, TXT, CSV, Excel, images (OCR), emails
- 🔍 Hybrid semantic + keyword search (vector similarity + BM25 fusion)
- 💬 Streaming AI chat with source citations, powered by LangGraph
- 📊 Summarization, document comparison, report generation, FAQ generation
- 🌐 Multilingual support (auto-detects question language)
- 📈 Admin dashboard with usage analytics and feedback tracking
- 🐳 Fully containerized with Docker Compose, CI/CD via GitHub Actions

## Tech Stack

**Backend:** FastAPI, LangGraph, LangChain, PostgreSQL, SQLAlchemy, Alembic
**AI:** Gemini API (free tier), sentence-transformers, ChromaDB, BM25
**Frontend:** React, TypeScript, Tailwind CSS, Vite
**Infra:** Docker, AWS (S3, EC2, Secrets Manager), GitHub Actions

## Local Setup

### Prerequisites
- Python 3.13+, Node.js 20+, Docker Desktop
- A free Gemini API key (https://aistudio.google.com/apikey)
- An AWS account (Free Tier is sufficient)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

cp ../.env.example ../.env      # fill in real values
docker compose up -d            # starts Postgres + ChromaDB

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`.

### Running Tests

```bash
cd backend
pytest -v
```

## Deployment

See `architecture/system_architecture.md` for system design details and
`scripts/deploy_ec2.sh` for AWS EC2 deployment steps.

## Project Structure
backend/          FastAPI application
frontend/          React application
architecture/     System design documentation
scripts/          Deployment and utility scripts
sample-data/       Test fixtures for document parsers
docs/             Additional documentation

## License

MIT — see LICENSE file.