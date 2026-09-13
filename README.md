<div align="center">

# 💊 AIVOA AI Pharma QMS

**Next-Generation Pharmaceutical Complaint Management System with LangGraph & Groq Inference**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-orange?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Ultra--Fast_Inference-f55036?style=for-the-badge)](https://groq.com/)
[![React](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Redux Toolkit](https://img.shields.io/badge/Redux_Toolkit-764ABC?style=for-the-badge&logo=redux)](https://redux-toolkit.js.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

*An interview-ready, human-in-the-loop pharmaceutical Quality Management System compliant with cGMP and 21 CFR Part 11 principles.*

> **Last Updated:** September 2026 (Updated after Antigravity LangGraph & Groq architectural integrations)

</div>

---

## 🌟 Overview

**AIVOA QMS** transforms the intake of chaotic pharmaceutical customer complaints (emails, scanned documents, verbal reports) into verified, audit-ready quality records.

Built with a **FastAPI** backend, a compiled **LangGraph** AI agent pipeline, **Groq ultra-fast LLM inference**, and a responsive **React 18 / Redux Toolkit** frontend, it delivers sub-second extraction, deterministic regulatory completeness scoring, clinical risk triage, CAPA generation, and an interactive AI Copilot.

---

## ✨ Key Technical Highlights

- 🧠 **Compiled LangGraph Pipeline:** True `StateGraph` executing 6 discrete nodes: `parse_document` ➔ `validate_completeness` ➔ `classify_risk` ➔ `check_duplicates` ➔ `generate_capa` ➔ `assemble`.
- ⚡ **Tiered Groq LLM Inference:**
  - `gemma2-9b-it` (temperature 0.1, JSON mode) for rapid structured 12-field extraction.
  - `llama-3.3-70b-versatile` (JSON mode) for deep clinical risk triage and CAPA generation citing FDA 21 CFR 211.198 and ICH Q10.
  - `llama-3.3-70b-versatile` for contextual AI Copilot investigation.
- 🛡️ **Zero-Crash Offline Fallbacks:** Deterministic regex parsing and keyword triage guarantee the system functions gracefully even without an active API key or internet connection.
- 📋 **Deterministic Regulatory Completeness:** Pure-Python scoring evaluating critical batch, customer, date, and description fields.
- 🔢 **Audit-Ready ID Sequencing:** Real database persistence generating sequential IDs: `CMP-YYYY-NNNN`.
- 🤝 **Strict Human-in-the-Loop:** AI assists the investigator; it never unilaterally commits data to the database without explicit human review.

---

## ⚙️ What Values I Need to Fill

To run the application locally or in production, configure the following environment variables.

### 1. Backend Environment Variables (`backend/.env`)

Create a file named `backend/.env` (or copy from `backend/.env.example`):

```bash
cp backend/.env.example backend/.env
```

| Variable Name | Required? | Default / Example Value | Where It Goes | What Happens If Missing / Left Blank |
|---|---|---|---|---|
| **`GROQ_API_KEY`** | **Optional** (Recommended for live AI) | `gsk_...` | `backend/.env` | **Graceful Fallback**: If blank, the system automatically uses deterministic regex parsing and keyword-based risk scoring. The application will **not** crash. If provided, enables live LLM extraction, risk scoring, CAPA generation, and Copilot chat. |
| **`DATABASE_URL`** | **Optional** | `sqlite:///./aivoa.db` | `backend/.env` | **Uses SQLite**: Defaults to a local SQLite database (`aivoa.db`). For PostgreSQL / pgvector, set: `postgresql+psycopg://user:pass@localhost:5432/aivoa`. |
| **`ALLOWED_ORIGINS`** | **Optional** | `http://localhost:5173,http://localhost:3000` | `backend/.env` | **CORS Control**: Comma-separated list of allowed frontend URLs. Defaults to `http://localhost:3000`. Set to `http://localhost:5173` for default Vite frontend. |
| **`APP_ENV`** | **Optional** | `development` | `backend/.env` | Sets application mode (`development` or `production`). |
| **`MODEL_EXTRACTION`** | **Optional** | `gemma2-9b-it` | `backend/.env` | Groq model used for rapid JSON field extraction. |
| **`MODEL_REASONING`** | **Optional** | `llama-3.3-70b-versatile` | `backend/.env` | Groq model used for clinical risk triage and CAPA generation. |
| **`ENABLE_FALLBACK_MOCKS`** | **Optional** | `True` | `backend/.env` | If True, app gracefully falls back to regex/rules if AI fails. Set to `False` in strict production. |
| **`DUPLICATE_SIMILARITY_THRESHOLD`**| **Optional** | `0.25` | `backend/.env` | The Jaccard token overlap similarity score required to flag a duplicate record. |

### 2. Frontend Environment Variables (`frontend/.env`)

Create a file named `frontend/.env` (or copy from `frontend/.env.example`):

```bash
cp frontend/.env.example frontend/.env
```

| Variable Name | Required? | Default / Example Value | Where It Goes | What Happens If Missing / Left Blank |
|---|---|---|---|---|
| **`VITE_API_URL`** | **Optional** | `http://localhost:8000/api/v1` | `frontend/.env` | **Uses localhost**: If omitted, Axios automatically defaults to `http://localhost:8000/api/v1`. If your backend runs on a different host/port, configure it here. |

---

## 🚀 Quickstart Guide

### Option A: Local Development Setup (Recommended)

#### 1. Start the Backend (FastAPI)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# (Optional) Add your Groq API key to backend/.env
echo "GROQ_API_KEY=your_actual_groq_api_key_here" >> .env
echo "ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000" >> .env

uvicorn app.main:app --reload --port 8000
```
*The API is now live at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.*

#### 2. Start the Frontend (React + Vite)
In a separate terminal window:
```bash
cd frontend
npm install
npm run start
```
*The UI is now live at `http://localhost:5173`.*

---

### Option B: Docker Compose Setup

Run the full stack with PostgreSQL and pgvector:
```bash
docker-compose up --build
```

---

## 🧪 Testing with Sample Files

Realistic pharmaceutical complaint scenarios are included in the [`samples/`](./samples) directory:
- `samples/sample_email_1.txt`: Hospital reporting particulate contamination in injectable vials (Critical Risk).
- `samples/sample_written_2.txt`: Clinic reporting packaging blister seal defects (Major Risk).
- `samples/sample_verbal_3.txt`: Doctor verbal report of adverse nausea reactions (High Risk).

Simply drag and drop any sample file into the **AI Intake Assistant** zone in the UI.

---

## 📚 Detailed Technical Documentation

For interview preparation, architectural diagrams, and video walkthrough scripts, refer to the documentation suite in [`docs/`](./docs):
- [**Architectural Changelog & Design Rationale**](./docs/CHANGELOG_EXPLANATION.md) — What was refactored, remaining fallbacks, and design trade-offs.
- [**End-to-End Code Walkthrough**](./docs/CODE_WALKTHROUGH.md) — Step-by-step trace from file drop to database commit.
- [**Product Requirements & Implementation Status**](./docs/PRD.md) — Exact feature breakdown: implemented vs. partial vs. future.
- [**Interview Questions & Answers**](./docs/INTERVIEW_QA.md) — Deep technical Q&A covering React, Redux, LangGraph, Groq, and 21 CFR Part 11.
- [**Video Demo Script**](./docs/VIDEO_SCRIPT_DEMO.md) — 5–7 minute script for screen-recorded UI walkthrough.
- [**Video Code Walkthrough Script**](./docs/VIDEO_SCRIPT_CODE_WALKTHROUGH.md) — 8–10 minute script for screen-recorded architectural code tour.

---

## 📄 License
This project is licensed under the MIT License.
