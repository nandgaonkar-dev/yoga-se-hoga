# yoga-se-hoga

A FastAPI backend that generates yoga routines with an LLM, using structured-output enforcement and retrieval-augmented generation over a curated pose knowledge base.

## What it does

- Generates a yoga routine (warm-up, main sequence, cool-down, safety notes) from a user's experience level, time available, goal, and optional injuries.
- Enforces the response shape with a strict JSON schema (Groq's structured output mode) validated against Pydantic models, with an automatic retry loop that feeds validation errors back into the prompt on failure.
- Grounds the routine in a curated, 20-pose knowledge base via retrieval: the user's goal and any stated injuries are embedded, matched against the knowledge base with a local vector search, and the retrieved poses (including their contraindications) are injected into the prompt instead of relying on the model's unaided guess.
- Persists every request (profile + generated routine) to SQLite.

## Architecture

```
app/
├── main.py               FastAPI app, the one live endpoint
├── models.py              Pydantic models + the JSON schema Groq is told to enforce
├── routine_service.py     RAG generation logic: retrieval, prompt construction, Groq call, retry loop
├── retrieval.py            Embeds a query and searches the Chroma collection
├── db.py                   SQLite persistence (user_profile, conversation_history)
├── embed_kb.py             Builds the Chroma collection from knowledge_base.json
├── knowledge_base.json     20 hand-curated poses (benefits, contraindications, difficulty)
└── legacy/
    └── routine_service_no_rag.py   Pre-RAG generation — not used by the live API, see below

evals/
└── eval_no_rag.py          Runs the non-RAG generator across fixed inputs, logs pass/fail + latency
```

The endpoint is a thin wrapper — all actual logic (retrieval, prompt building, the Groq call, retries) lives in plain functions in `routine_service.py`, callable with no HTTP involved. `evals/` imports those functions directly, so eval harnesses exercise the same code the API runs, not a separate copy.

**A note on the knowledge base**: `knowledge_base.json` was authored for this project (with AI assistance), not sourced from a certified yoga or physical-therapy reference. It's built to be internally consistent and to exercise the retrieval pipeline realistically, but it isn't a validated safety dataset. What this project demonstrates is the RAG mechanism — embedding, vector search, retrieval-grounded generation — not a claim that the specific guidance it retrieves is authoritative.

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # or source venv/bin/activate on Linux/macOS
pip install -r requirements.txt
```

Create a `.env` file in the repo root with:
```
GROQ_API_KEY=your_key_here
```

Build the vector store (run once, or whenever `knowledge_base.json` changes):
```bash
python -m app.embed_kb
```

Run the API:
```bash
uvicorn app.main:app --reload
```

## Endpoint

| Endpoint | Body | Behavior |
|---|---|---|
| `POST /generate_routine_rag` | `experience_level`, `time_available` (5-60 min), `goal`, optional `injuries` | Retrieves the 5 most relevant poses from the knowledge base, grounds the routine in them, persists the request to SQLite. Returns `{routine, retrieved_poses}`. |

## Incremental development

`app/legacy/routine_service_no_rag.py` is the older implementation — structured output and the retry loop, no retrieval — kept as a reference point for how the project evolved rather than as a live code path.