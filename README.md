# Local Text-to-SQL AI Agent 🚀

A high-privacy, fully offline Text-to-SQL execution pipeline that translates natural language questions into syntactically correct, case-sensitive PostgreSQL queries. Powered by **Llama 3.1 (8B)** served locally via **Ollama**, this agent bridges the gap between natural language and structured databases without letting your sensitive schema or data leave your local infrastructure.

---

## ✨ Features

- **100% Local & Private:** Zero API costs, zero data privacy risks. Everything runs entirely on your local machine.
- **Case-Sensitive Schema-Awareness:** Implements robust context injection ensuring the model strictly adheres to PostgreSQL's case-sensitive column formatting (automatic double-quoting rules).
- **Asynchronous Database Execution:** Built using Python's `asyncio` and `SQLAlchemy` asynchronous engines for fast, concurrent database operations.
- **Intelligent Result-Set Management:** Dynamically truncates, formats, and displays wide database outputs cleanly in the terminal to avoid buffer overflows while still reporting the exact total row count.

---

## 🛠️ Tech Stack

- **LLM Engine:** Ollama / Llama 3.1 (8B)
- **Database:** PostgreSQL (ClassicModels Sample Schema)
- **Database Toolkit:** SQLAlchemy (Async) & `psycopg2-binary`
- **Orchestration:** Python 3.10+ & AsyncIO
- **Environment:** `python-dotenv` for secure database credential mapping

---

## 🏗️ Architecture Workflow

1. **User Query Input:** Captures user questions (e.g., *"What is the MSRP of our most expensive motorcycle?"*).
2. **Context Assembly:** Injects the static schema definition (including specific case-sensitive column names) into a strict developer-guided prompt.
3. **Local Inference:** Llama 3.1 (8B) synthesizes the schema context and generates a precise, executable raw PostgreSQL query.
4. **Asynchronous Execution:** The Python pipeline extracts the clean SQL code block and runs it asynchronously against the PostgreSQL engine.
5. **Result-Set Post-Processing:** Python intercepts the raw database tuples, counts the total records, truncates the output to the top 5 entries, and displays them vertically or in clean tabular grids.
