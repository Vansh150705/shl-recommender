# Approach Document — SHL Assessment Recommender

## What I Built and Why

When I first read the problem, the core challenge was clear: most assessment catalogues assume the user already knows what they want. A hiring manager who says "I need something for a Java developer" doesn't know if they mean a knowledge test, a coding simulation, or a personality measure. The agent needs to figure that out through conversation.

I built a FastAPI service that takes the full conversation history on every call, retrieves the most relevant assessments from the SHL catalog, and uses an LLM to drive the dialogue — clarifying when needed, recommending when ready, and refusing anything off-topic.

---

## Architecture

The system has three moving parts:

**1. Keyword Retrieval**
When a request comes in, I score every catalog item against the conversation text using a combination of direct name matching (high weight), description/keyword matching, and category-based boosting. This returns 12 candidate items in under 5ms — no vector database, no embedding API call.

I deliberately chose keyword retrieval over embeddings. The catalog has ~120 items, which is small enough to score exhaustively. Embedding calls would add 300–800ms of latency on every request, pushing dangerously close to the 30-second timeout when combined with the LLM call. Keeping retrieval fast and local was the right trade-off here.

**2. Prompt Engineering**
The retrieved catalog items are injected as structured snippets (name, URL, type, job levels, duration, description) directly into the prompt. The system prompt enforces four behaviors: clarify vague queries before recommending, recommend 1–10 items once context is clear, update the shortlist when constraints change mid-conversation, and refuse anything outside SHL assessments.

I set temperature to 0.2 to keep the JSON output consistent and reduce the chance of the model going off-format.

**3. Hallucination Guard**
Every URL in the model's response is validated against the catalog before being returned. If a name matches a catalog item, I replace whatever URL the model gave with the real one. If neither the name nor URL matches anything in the catalog, the item is silently dropped. This gives a hard guarantee: the API never returns a URL that isn't in the real SHL catalog.

---

## Retrieval Design

The scoring logic works like this:
- +3 points if a query word appears in the item name
- +1 point for each query word found in the description, keys, or job levels
- +2 points category boost when a known domain (java, personality, cognitive, etc.) appears in both the query and the item

This means "hiring a mid-level Java developer" naturally surfaces Java knowledge tests, while "leadership potential executive" surfaces OPQ and scenario-based tests. For ambiguous queries, the fallback adds diverse items spanning different test types.

---

## Dialogue Logic

The agent is designed to handle four conversation patterns:

- **Clarify:** On a vague first message, ask one focused question (role? level? what to measure?)
- **Recommend:** Once role + context is clear, commit to a shortlist of 1–10 items with names and URLs
- **Refine:** When the user changes constraints ("add personality tests", "actually senior level"), update the existing shortlist rather than starting over
- **Compare:** When asked about differences between assessments, answer from the catalog data injected in the prompt — not from the model's training knowledge

The turn cap (8 turns) is enforced server-side by slicing the messages array. By turn 4, the system prompt instructs the model to commit to a recommendation even with partial information.

---

## What Didn't Work

**Embeddings-based retrieval** — I tried using sentence embeddings for retrieval early on. Recall improved on abstract queries like "leadership potential" but latency went up significantly. With the 30-second timeout constraint, the safer choice was keyword retrieval.

**Injecting the full catalog into the prompt** — My first version sent all 120 items as context. This burned tokens fast, hit rate limits immediately, and made the prompt unwieldy. Limiting to 12 retrieved candidates fixed both problems.

**Pinned package versions on Python 3.14** — The initial deploy on Render failed because Python 3.14 doesn't have pre-built wheels for pinned older packages. Fixed by adding a `runtime.txt` specifying Python 3.11 and unpinning versions in requirements.

---

## Stack

- **LLM:** Groq (llama-3.3-70b-versatile) — fast, free tier with generous limits, no quota issues
- **Framework:** FastAPI — native async, auto Pydantic validation, auto-generated docs at /docs
- **Retrieval:** In-memory keyword scoring — fast, transparent, zero external dependencies
- **Deployment:** Render free tier — matches the 2-minute cold-start allowance in the spec
- **AI tools used:** Claude for code assistance during development. All design decisions, trade-offs, and debugging were my own.