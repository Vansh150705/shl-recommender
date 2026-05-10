# SHL Assessment Recommender

Conversational FastAPI agent that recommends SHL assessments through dialogue.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Readiness check → `{"status": "ok"}` |
| POST | `/chat` | Conversational recommender |

## Quick Start (Local)

```bash
# 1. Clone & install
pip install -r requirements.txt

# 2. Set your Gemini API key
export GEMINI_API_KEY=your_key_here

# 3. Run
uvicorn main:app --reload --port 8000

# 4. Test
python3 test_chat.py
```

## Deploy to Render (Free)

1. Push this repo to GitHub
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Set these:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `GEMINI_API_KEY` = your key
6. Deploy → your URL will be `https://your-app.onrender.com`

## API Usage

```bash
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hiring a mid-level Java developer who works with stakeholders"}
    ]
  }'
```

### Response Schema
```json
{
  "reply": "Here are assessments that fit...",
  "recommendations": [
    {"name": "Java 8 (New)", "url": "https://www.shl.com/...", "test_type": "K"}
  ],
  "end_of_conversation": false
}
```

`test_type` codes: K=Knowledge, P=Personality, A=Ability, S=Simulation, C=Competency, B=Biodata, D=Development

## Get Gemini API Key

1. Go to https://aistudio.google.com
2. Click "Get API Key" → "Create API key"
3. Copy the key
