# Local RAG POC — 10-Minute Team Walkthrough

> A plain-English tour of what this service does, how it's built, and where LLM
> tokens (and cost) actually get spent. No prior RAG knowledge assumed.

---

## 0. The one-sentence summary (30 sec)

> We take a PDF, break it into small pieces, store those pieces in a local
> searchable database, and when someone asks a question we find the most
> relevant pieces and ask an LLM to answer **using only those pieces**.

That pattern is called **RAG — Retrieval-Augmented Generation**. "Retrieval" =
find the relevant text. "Generation" = the LLM writes the answer. The point is
the LLM answers from *our documents*, not from its own memory.

---

## 1. Clearing up two myths first (1 min)

Worth saying out loud because the names get thrown around:

- **No LlamaIndex / LangChain.** People assume every RAG app uses one of those
  frameworks. This one does **not**. It's built from small, readable libraries
  (`pypdf`, `sentence-transformers`, `chromadb`). Less magic, easier to debug.
- **The LLM here is Google Gemini, not Claude.** Generation runs on
  `gemini-2.5-flash`. So when we talk about "tokens" below, those are **Gemini
  API tokens**. (Embeddings are a different, local model — more on that next.)

---

## 2. The two APIs (1 min)

It's one FastAPI app with two endpoints (`app/main.py`):

| Endpoint   | What it does                                  | When you call it          |
|------------|-----------------------------------------------|---------------------------|
| `POST /ingest` | Load a PDF → chunk → embed → store         | Once per document         |
| `POST /query`  | Question → find chunks → LLM answers       | Every time someone asks   |
| `GET /health`  | "am I alive?"                              | Monitoring                |

Key mental model: **Ingest is the one-time setup. Query is the repeated use.**

---

## 3. The Ingest pipeline — step by step (3 min)

Code: `app/routers/ingest.py`. Four stages:

**1. Read the PDF** — `services/pdf.py`
Pulls text out page by page with `pypdf`. Keeps the page number with each page
(so we can cite it later). Pages with no extractable text are skipped.

**2. Chunk it** — `services/chunking.py`
We can't store a whole PDF as one blob — search would be useless and it wouldn't
fit in a prompt. So we cut each page into overlapping pieces:
- ~**800 characters** per chunk
- **150 characters of overlap** between neighbors (so a sentence split across a
  boundary isn't lost)
- It never splits mid-word.

**3. Embed each chunk** — `services/embeddings.py`  ← *important for cost talk*
Each chunk is turned into a **vector** (a list of ~384 numbers) that captures its
meaning. Chunks about similar topics get similar vectors. This is done by a
**local model** — `sentence-transformers/all-MiniLM-L6-v2` — that runs **on our
own machine**. **No API call, no token cost, no data leaves the box.**

**4. Store it** — `services/vectorstore.py`
The chunk text + its vector + metadata (source filename, page number) go into
**ChromaDB**, a local vector database that saves to `./data/chroma` on disk. So
it survives restarts — you ingest a PDF once.

Output you get back: `{ source, pages, chunks_added }`.

---

## 4. The Query pipeline — step by step (3 min)

Code: `app/routers/query.py`. This is where the LLM (and tokens) come in.

**1. Embed the question**
The user's question goes through the *same local embedding model* into a vector.
Still local, still free.

**2. Search the vector DB**
ChromaDB compares the question's vector to all stored chunk vectors and returns
the **top-k closest** (default **k=4**). This is "semantic search" — it matches
on *meaning*, not keywords.

**3. Ask the LLM** — `services/llm.py`  ← *this is the only step that costs money*
We build a prompt that looks like:

```
SYSTEM: Answer ONLY from the CONTEXT. If it's not there, say "I can't answer
        that from the provided documents." Cite as [source, page N].

CONTEXT:
[RFE letter, page 3]
<chunk text...>

[RFE letter, page 5]
<chunk text...>
...(the 4 retrieved chunks)...

QUESTION: <the user's question>
```

We send that to **Gemini at temperature 0** (deterministic, no creativity) and
return its answer.

**4. Ground-check + citations**
If the model returns the refusal sentence, we mark `grounded: false` and return
no citations. Otherwise we attach which source/page each chunk came from.

Output: `{ answer, grounded, citations[] }`.

---

## 5. Where do tokens get used? (1.5 min) — the part people ask about

A **token** is roughly ¾ of a word; LLM APIs bill per token in + per token out.
Here's the honest breakdown:

| Step                         | Uses LLM tokens? | Cost                      |
|------------------------------|------------------|---------------------------|
| PDF reading                  | No               | Free (local)              |
| Chunking                     | No               | Free (local)             |
| **Embedding (ingest+query)** | **No**           | Free — local model        |
| Vector search                | No               | Free (local DB)           |
| **Generation (`/query`)**    | **YES — Gemini** | Paid, per call            |

So **the only thing that spends tokens is the final answer step in `/query`.**
Ingesting a 100-page PDF costs **zero** tokens. Each question costs tokens.

**What's in the bill for one question:**
- **Input tokens** = system instruction + the 4 retrieved chunks + the question.
  The chunks dominate: 4 × ~800 chars ≈ **~900–1,000 input tokens**, plus
  question and instructions.
- **Output tokens** = however long the answer is.

**Practical levers if cost matters:**
- Lower `top_k` (fewer chunks → fewer input tokens) — `config.py`
- Smaller `chunk_size`
- `gemini-2.5-flash` is already the cheap/fast tier
- Ingest is free, so re-ingesting documents is never the cost problem — questions are.

---

## 6. Config knobs to know (30 sec)

All in `app/config.py` / `.env`:

- `chunk_size` (800), `chunk_overlap` (150) — how PDFs get cut
- `top_k` (4) — how many chunks feed the LLM (biggest cost/quality lever)
- `embedding_model` — the local, free embedder
- `gemini_model` (gemini-2.5-flash), `gemini_api_key` — the paid LLM
- `refusal_message` — exact sentence the model says when the answer isn't in the docs

---

## 7. Live demo script (if you have a minute left)

```bash
# start it
uvicorn app.main:app --reload

# ingest the sample PDF (one-time, free)
curl -X POST localhost:8000/ingest \
  -H 'content-type: application/json' \
  -d '{"path": "Compressed RFE letter (2).pdf"}'

# ask a question (this one spends Gemini tokens)
curl -X POST localhost:8000/query \
  -H 'content-type: application/json' \
  -d '{"question": "What does the letter ask for?"}'
```

Point out in the response: the `answer`, `grounded: true`, and the `citations`
showing source + page. Then ask something *not* in the PDF to show the refusal.

---

## TL;DR for the team

1. It's **RAG**: store document pieces, retrieve the relevant ones, let an LLM
   answer from them only.
2. **Hand-built, no LlamaIndex** — just small libraries, easy to read.
3. **Embeddings + search are local and free.** Only the **Gemini** answer step
   costs tokens, and only on `/query`.
4. **Ingest once (free), query many times (paid).**
