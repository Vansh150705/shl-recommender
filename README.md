# SHL Assessment Recommender

A conversational API that helps hiring managers find the right SHL assessments through dialogue. Instead of keyword search, it asks clarifying questions and builds a shortlist based on role, seniority, and what you want to measure.

## Live API

**Base URL:** `https://shl-recommender-v59v.onrender.com`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns `{"status": "ok"}` |
| `/chat` | POST | Conversational recommender |
| `/docs` | GET | Interactive Swagger UI |

---

## How It Works ?

Send the full conversation history on every call. The API is stateless — no session is stored server-side.

**Request:**
```json
POST /chat
{
  "messages": [
    {"role": "user", "content": "Hiring a mid-level Java developer who works with stakeholders"},
    {"role": "assistant", "content": "What seniority level and experience range are you targeting?"},
    {"role": "user", "content": "Around 4 years experience, needs strong OOP and communication skills"}
  ]
}
```

**Response:**
```json
{
  "reply": "Here are assessments that fit a mid-level Java developer with stakeholder interaction needs.",
  "recommendations": [
    {
      "name": "Core Java (Advanced Level) (New)",
      "url": "https://www.shl.com/products/product-catalog/view/core-java-advanced-level-new/",
      "test_type": "K"
    },
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/products/product-catalog/view/java-8-new/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": false
}
```

**test_type codes:**
- `K` = Knowledge & Skills
- `P` = Personality & Behavior
- `A` = Ability & Aptitude
- `S` = Simulations
- `C` = Competencies
- `B` = Biodata & Situational Judgment
- `D` = Development & 360

`recommendations` is empty `[]` when the agent is still gathering context. `end_of_conversation` is `true` only when the task is complete.

---

## Run Locally

```bash
# Clone and install
git clone https://github.com/Vansh150705/shl-recommender
cd shl-recommender
pip install -r requirements.txt

# Set your Groq API key (get one free at console.groq.com)
set GROQ_API_KEY=your_key_here   # Windows
export GROQ_API_KEY=your_key_here  # Mac/Linux

# Start the server
uvicorn main:app --reload --port 8000
```

Test it:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hiring a Java developer"}]}'
```

---

## Agent Behavior

- **Clarifies** vague queries before recommending — "I need an assessment" gets a clarifying question, not a premature shortlist
- **Recommends** 1–10 assessments with real catalog URLs once there's enough context
- **Refines** the shortlist when constraints change mid-conversation ("actually add a personality test")
- **Compares** assessments using catalog data, not hallucinated knowledge
- **Refuses** off-topic requests — general hiring advice, legal questions, prompt injection attempts
- **Caps** at 8 turns per conversation as required

---

## Project Structure

```
shl-recommender/
├── main.py          # FastAPI app — retrieval, prompt, Groq call, validation
├── catalog.json     # 121 SHL Individual Test Solutions
├── requirements.txt
├── runtime.txt      # Python 3.11
├── render.yaml      # Render deployment config
└── APPROACH.md      # Design decisions and trade-offs
```