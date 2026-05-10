# SHL Assessment Recommender — Approach Document

**Candidate:** AI Intern Application | **Stack:** Python · FastAPI · Gemini 2.0 Flash · Keyword Retrieval

---

## 1. Problem Decomposition

The core challenge is moving a user from a vague hiring intent to a grounded shortlist through dialogue, without hallucinating assessments. I decomposed this into four sub-problems:

- **Retrieval** — given a natural-language query, which catalog items are candidates?
- **Dialogue management** — when to clarify, when to recommend, when to refuse
- **Grounding** — ensuring every URL and name in the output comes from the real catalog
- **Schema compliance** — every response must match the exact JSON spec

---

## 2. Architecture

```
POST /chat (stateless)
      │
      ▼
Keyword Retrieval  ──►  Top-20 catalog items
      │
      ▼
Prompt Builder  ──►  System prompt + catalog snippets + full conversation history
      │
      ▼
Gemini 2.0 Flash  ──►  JSON response
      │
      ▼
URL Validator  ──►  Strip hallucinated items, keep only catalog-verified URLs
      │
      ▼
ChatResponse  ──►  reply + recommendations[] + end_of_conversation
```

**Stateless design:** the full conversation history is sent on every call. No per-session state is stored server-side, exactly as specified.

---

## 3. Retrieval Setup

I chose **keyword-based retrieval** over a vector store for three reasons:
- The catalog (~120 items) is small enough to score exhaustively in <5ms
- No external dependency (no Chroma, FAISS, or embedding API call) keeps cold-start fast and stays well within the 30-second timeout
- Transparent scoring makes hallucination easier to prevent

**Scoring logic:**
- +3.0 if query word appears in the item **name** (high signal)
- +1.0 for each query word appearing in description/keys/levels
- +2.0 category boost when a known keyword category (e.g. "java", "personality", "cognitive") appears in both query and item text

This returns 15–25 candidates which are injected into the Gemini prompt as structured context.

---

## 4. Prompt Design

The system prompt enforces four hard constraints:

1. **Clarify before recommending** on vague queries (turn 1 with no role/level/goal)
2. **Recommend 1–10 items** once role + measurement goal is clear
3. **Refine, don't restart** when user changes constraints mid-conversation
4. **Refuse off-topic** requests (general hiring advice, legal, prompt injection)

The catalog context is injected as structured snippets (Name, URL, Type, Levels, Duration, Description) so Gemini can answer comparison questions from data rather than prior knowledge.

**Temperature = 0.2** keeps responses deterministic and schema-compliant.

---

## 5. Hallucination Prevention

Every URL in the response is validated against the catalog before being returned. If Gemini returns a name or URL not in the catalog, it is silently dropped. This gives a hard guarantee: **the API never returns a URL that isn't in the SHL catalog.**

---

## 6. Evaluation Approach

I tested against the three scoring criteria:

**Hard evals (schema compliance):**
- Ran automated tests for every response shape — verified `recommendations`, `reply`, `end_of_conversation` are always present and correctly typed
- Verified vague queries return `recommendations: []`
- Verified turn cap (8) is enforced server-side by slicing the messages array

**Recall@10:**
- Tested 6 personas manually (Java developer, Data Scientist, Sales Manager, Entry-Level Customer Service, Senior Leader, General Cognitive)
- Measured whether expected assessments appeared in top-10 results
- Retrieval recall was highest for tech roles (Java, Python) and lowest for abstract roles ("leadership potential") — mitigated by including personality and cognitive tests as defaults for ambiguous roles

**Behavior probes:**
- Off-topic refusal: ✅ reliably refused general hiring advice
- No premature recommendation: ✅ vague "I need an assessment" triggers clarification
- Refinement honored: ✅ "add personality tests" updates shortlist in-place
- Comparison grounded: ✅ OPQ vs GSA comparison pulls from catalog descriptions

---

## 7. What Didn't Work

- **Embedding-based retrieval (early attempt):** using `text-embedding-004` improved recall on abstract queries but added ~800ms latency per call and required an extra API round-trip, risking the 30s timeout. Dropped in favour of keyword retrieval.
- **Single-turn prompting:** early versions asked Gemini to handle both retrieval and ranking in one prompt. This caused the model to occasionally recommend items it inferred from training data rather than the provided context. Fixed by injecting catalog snippets explicitly and adding URL validation.

---

## 8. Stack Justification

| Component | Choice | Reason |
|-----------|--------|--------|
| LLM | Gemini 2.0 Flash | Free tier, fast, 1M context window fits entire catalog |
| Framework | FastAPI | Native async, auto schema validation via Pydantic |
| Retrieval | Keyword scoring | Fast, transparent, no external deps |
| Deployment | Render (free) | Matches the 2-min cold-start allowance in spec |
| AI tools used | Claude (code assistance), Gemini (runtime LLM) | Used for code generation; all design decisions and trade-offs are my own |
