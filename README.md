# Local Text-to-SQL AI Agent 🚀
# Customer API + Local Text2SQL Agent

A high-privacy, fully offline Text-to-SQL execution pipeline that translates natural language questions into syntactically correct, case-sensitive PostgreSQL queries. Powered by **Llama 3.1 (8B)** served locally via **Ollama**, this agent bridges the gap between natural language and structured databases without letting your sensitive schema or data leave your local infrastructure.
A FastAPI service backed by PostgreSQL that combines:
- **Dashboard APIs** for key table counts
- A **local LLM-powered Text2SQL endpoint** that translates natural-language questions into SQL, executes the query, and returns a plain-language summary

---
This project is designed for local-first experimentation with the ClassicModels-style schema and an Ollama-hosted model.

## ✨ Features
## What this project does

- **100% Local & Private:** Zero API costs, zero data privacy risks. Everything runs entirely on your local machine.
- **Case-Sensitive Schema-Awareness:** Implements robust context injection ensuring the model strictly adheres to PostgreSQL's case-sensitive column formatting (automatic double-quoting rules).
- **Asynchronous Database Execution:** Built using Python's `asyncio` and `SQLAlchemy` asynchronous engines for fast, concurrent database operations.
- **Intelligent Result-Set Management:** Dynamically truncates, formats, and displays wide database outputs cleanly in the terminal to avoid buffer overflows while still reporting the exact total row count.
- Serves REST endpoints with **FastAPI**
- Uses **async SQLAlchemy** + **asyncpg** for database access
- Runs a **local SQL generation agent** against an Ollama model (`llama3.1:8b`)
- Enforces a simple SQL safety guardrail (read-only `SELECT` queries)
- Retries SQL generation up to 3 times using error-aware correction prompts
- Returns both raw results and a natural-language summary

---
## Architecture overview

## 🛠️ Tech Stack
1. Client calls `/agent/sql` with a question.
2. `sql_agent.py` builds a strict schema-aware prompt.
3. Ollama generates SQL.
4. SQL is cleaned/sanitized (`clean_sql`).
5. Guardrail blocks non-`SELECT` statements.
6. Query runs against PostgreSQL via async engine.
7. A second Ollama prompt summarizes result data.
8. API returns `sql`, `result`, `summary`, and `status`.

- **LLM Engine:** Ollama / Llama 3.1 (8B)
- **Database:** PostgreSQL (ClassicModels Sample Schema)
- **Database Toolkit:** SQLAlchemy (Async) & `psycopg2-binary`
- **Orchestration:** Python 3.10+ & AsyncIO
- **Environment:** `python-dotenv` for secure database credential mapping
## Tech stack

---
- **Python** 3.10+
- **FastAPI** + Uvicorn
- **SQLAlchemy 2.x** (async)
- **PostgreSQL** (Docker Compose)
- **Ollama** local inference
- **Pydantic v2**

## 🏗️ Architecture Workflow
## Repository structure

1. **User Query Input:** Captures user questions (e.g., *"What is the MSRP of our most expensive motorcycle?"*).
2. **Context Assembly:** Injects the static schema definition (including specific case-sensitive column names) into a strict developer-guided prompt.
3. **Local Inference:** Llama 3.1 (8B) synthesizes the schema context and generates a precise, executable raw PostgreSQL query.
4. **Asynchronous Execution:** The Python pipeline extracts the clean SQL code block and runs it asynchronously against the PostgreSQL engine.
5. **Result-Set Post-Processing:** Python intercepts the raw database tuples, counts the total records, truncates the output to the top 5 entries, and displays them vertically or in clean tabular grids.
```text
.
├── main.py               # FastAPI app bootstrap
├── router.py             # API routes (/overall_counts, /customers/count, /agent/sql)
├── sql_agent.py          # Prompting, SQL generation, execution, retries, summarization
├── database.py           # Async engine/session setup
├── models.py             # Minimal SQLAlchemy models for core tables
├── crud.py               # Async count query helpers
├── logger.py             # Console + file logger (app.log)
├── docker-compose.yml    # PostgreSQL service
├── seed.sql              # Database seed script mounted into Postgres init
├── evaluate_all.py       # Batch benchmark runner for SQL questions
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variable template
```

## Prerequisites

- Docker + Docker Compose
- Python 3.10+
- Ollama installed locally

## Local setup

### 1) Configure environment variables

Create `.env` in the project root using `.env.example`:

```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
POSTGRES_PORT=5432
DB_HOST=localhost
```

> `database.py` builds the DB URL from these `POSTGRES_*` values.
### 2) Start PostgreSQL with seed data

```bash
docker compose up -d
```

This launches `postgres:17-alpine` and runs `seed.sql` on first initialization.

### 3) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell
```

### 4) Install dependencies

```bash
pip install -r requirements.txt
```

### 5) Start Ollama model

```bash
ollama pull llama3.1:8b
ollama run llama3.1:8b
```

The API expects Ollama at `http://localhost:11434`.

### 6) Run the API

```bash
uvicorn main:app --reload
```

Open:
- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`

## API endpoints

### `GET /`
Health-style root message.

### `GET /overall_counts`
Runs 8 count queries concurrently and returns counts for:
- customers
- orders
- products
- employees
- offices
- payments
- orderdetails
- productlines

Also includes a `performance_metrics` duration string.

### `GET /customers/count`
Returns customer row count only.

### `POST /agent/sql`
Executes the local Text2SQL flow.

Request:
```json
{
  "question": "Which customer made the highest total payments?"
}
```

Response shape:
```json
{
  "sql": "SELECT ...;",
  "result": [["Euro+ Shopping Channel", 715738.98]],
  "summary": "Euro+ Shopping Channel has the highest total payment amount.",
  "status": "success"
}
```

On blocked/malicious intent, `status` is `failed` and SQL is `BLOCKED_BY_GUARDRAIL`.

## Evaluation script

`evaluate_all.py` runs benchmark questions from `sql_questions.csv` and writes `evaluation_report.csv`.

Run:

```bash
python evaluate_all.py
```

Expected input file:
- `sql_questions.csv` with a `question` column in the repo root.

## Logging

Logs are written to:
- stdout
- `app.log`

Useful for tracing:
- generation attempts
- SQL execution time
- retry/failure behavior

## Notes and limitations

- The SQL safety check currently allows only queries that start with `SELECT`.
- Prompt schema context is static in `sql_agent.py`; schema drift requires manual updates.
- LLM quality depends on local model behavior and prompt adherence.
- `evaluate_all.py` assumes `sql_questions.csv` exists.

## License

This project is licensed under the MIT License (./LICENSE)..
