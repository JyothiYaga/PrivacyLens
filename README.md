# PrivacyLens

A grounded Q&A assistant for **India's DPDP Act 2023** and the **EU GDPR**, built end to end on **Databricks Free Edition**. Every answer cites the exact article or section it came from.

> Educational project. Not legal advice.

## The problem

A product engineer building features that touch personal data must follow two laws: GDPR (88 pages) and the DPDP Act (21 pages). Reading them is slow, general chatbots answer without sources, and lawyers are expensive for everyday questions.

PrivacyLens answers questions such as *"Can a user make a company delete their data?"* in a few sentences, citing for example **GDPR Article 17** and **DPDP Section 12**, so the answer can be checked in seconds. Questions outside the two laws are refused instead of answered from guesswork. The assistant is deployed as a Databricks App with a feedback loop.

## Architecture

| Phase | What it does | Databricks components |
|---|---|---|
| 1. Prepare & govern data | PDFs in a Volume → bronze (one row per page) → silver (210 chunks split by article/section, with citation metadata). A Job runs the pipeline on file arrival and fails if the chunk counts are wrong | Unity Catalog, Volumes, Delta Lake, Change Data Feed, Lakeflow Jobs |
| 2. Vector index | Delta Sync index with managed embeddings (`databricks-gte-large-en`), synced as the last Job task | AI Search |
| 3. Retrieval | Meaning-based (ANN) search, 3 chunks per law, optional law filter | AI Search Python SDK |
| 4. Generation | Llama 3.3 70B answers only from retrieved chunks, cites each one, refuses off-topic questions. Packaged as an MLflow model with tracing and validated in a fresh environment | Foundation Model APIs, MLflow models, MLflow Tracing |
| 5. Registration | System prompt versioned in the Prompt Registry; model registered in Unity Catalog with the alias `champion`, with the prompt version pinned inside | MLflow Prompt Registry, Unity Catalog model registry |
| 7a. Evaluation | 30-question exam with code scorers and LLM judges; graders verified before trusting the baseline | MLflow GenAI evaluation |
| 6. Deployment | Serving endpoint (CPU, scale to zero) behind AI Gateway with inference tables, usage tracking and rate limits; Lakebase stores chats and feedback; Streamlit Databricks App for users | Model Serving, AI Gateway, Lakebase (Postgres), Databricks Apps |
| 7b. Improvement | *Next:* targeted fixes measured against the evaluation baseline | MLflow evaluation |

## Evaluation baseline

Model version 2 with prompt version 1, on 30 questions (7 GDPR-only, 7 DPDP-only, 8 comparison, 4 specific-detail, 4 off-topic traps):

| Scorer | Score |
|---|---|
| Citation valid (no invented citations) | 100% |
| No hedged citations | 100% |
| Grounded (LLM judge) | 97% |
| Correct refusal | 97% |
| Retrieval hit | 93% |
| Citation recall | 93% |
| Correct, key facts present (LLM judge) | 73% |

The first run reported 83% citation recall; reading the failures showed the scorer rejected valid forms such as `[GDPR Article 4(1)]`, and two answer keys were wrong. The grader was fixed before the baseline was recorded.

**What the baseline shows:** the writer is grounded but sometimes incomplete (it leaves out conditions), it once stated a penalty figure from outside knowledge, and long sections such as DPDP Section 2 (definitions) and Section 29 (appeals) are hard to retrieve. These are the targets for Phase 7b.

## Key design decisions

- **Structure-based chunking.** Chunks follow the laws' own articles and sections, and each chunk starts with its citation label, so retrieval and citations stay aligned.
- **Data quality gate.** The pipeline fails unless it finds exactly 99 GDPR articles and 45 DPDP units (44 sections plus the penalty Schedule). This check caught two real parsing bugs.
- **Measured retrieval choice.** On 5 test questions with 10 expected articles, meaning-based search found 10/10 while hybrid search found 6–7/10, because common words pulled the wrong articles up.
- **Balanced retrieval.** Three chunks from each law, so comparison questions never lose one law.
- **Grounded generation.** The model answers only from retrieved text and uses a fixed refusal sentence when the text does not cover the question.
- **Pinned prompts.** Each model version stores the exact prompt version it was logged with, so every evaluation score maps to one prompt and one model.
- **Feedback with privacy in mind.** Lakebase stores each chat with the model version, so user ratings can be compared across versions, and uses a random session ID instead of user identity (data minimisation).

## Repository structure

| File | Purpose |
|---|---|
| `01_ingest` | Create the schema and volume |
| `02_bronze` | Extract page text from the PDFs |
| `03_silver` | Clean, split by article/section, quality gate, Change Data Feed |
| `04_sync_index` | Trigger the vector index sync |
| `05_retrieve` | Retrieval experiments (ANN vs hybrid) and decision |
| `06_generate` | Prompt, tracing, model logging and validation |
| `07_register` | Prompt Registry, model registration, `champion` alias |
| `08_evaluate` | Evaluation exam, scoring and failure analysis |
| `retrieval.py` | Reusable retrieval functions |
| `privacylens_model.py` | MLflow model definition |
| `exam_set.py` | The 30-question evaluation set with answer keys |
| `scorers.py` | Code scorers and LLM-judge scorers |
| `app/` | Streamlit Databricks App (`app.py`, `app.yaml`, `requirements.txt`) |

## Data sources

- GDPR: Regulation (EU) 2016/679, from EUR-Lex.
- DPDP Act 2023: Gazette of India text.

## Status

Phases 1–6 and the evaluation baseline (7a) are complete; the app is deployed and collecting feedback. Next: Phase 7b improvements, each measured against the baseline.