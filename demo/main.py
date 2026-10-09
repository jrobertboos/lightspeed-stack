import os
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import httpx

app = FastAPI()

LCS_BASE_URL = os.environ.get("LCS_BASE_URL", "http://localhost:8080")

# Headers that must not be blindly forwarded between hops.
HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length", "content-encoding",
}

class Question(BaseModel):
    question: str
    conversation_id: str | None = None

CHAT_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>JRs LCORE Chat</title>
<style>
  body { font-family: sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
  #log { border: 1px solid #ccc; border-radius: 8px; padding: 1rem; min-height: 300px; margin-bottom: 1rem; white-space: pre-wrap; }
  .msg { margin-bottom: 0.75rem; }
  .me { color: #0b5fff; }
  .bot { color: #333; }
  .tools { color: #666; font-size: 0.8rem; white-space: normal; }
  form { display: flex; gap: 0.5rem; }
  input { flex: 1; padding: 0.5rem; }
  button { padding: 0.5rem 1rem; }
  #actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 1rem; }
  #actions button { font-size: 0.85rem; }
  .hint { color: #666; font-size: 0.9rem; margin: 0 0 1rem; }
</style>
</head>
<body>
<h1>JRs LCORE Chat</h1>
<p class="hint">Try a skill action. Look for a telltale in the reply (Allergen gate / Split card / Notes: now-next-need) and the tool line under it.</p>
<div id="actions"></div>
<div id="log"></div>
<form id="form">
  <input id="input" autocomplete="off" placeholder="Ask something..." />
  <button type="submit">Send</button>
</form>
<script>
const log = document.getElementById('log');
const form = document.getElementById('form');
const input = document.getElementById('input');
const actions = document.getElementById('actions');
let conversationId = null;

const ACTIONS = [
  {
    label: 'Allergen gate',
    text: "I'm making fried chicken and a sesame slaw. My guest is allergic to sesame. If I just leave the slaw off their plate, are they safe?",
  },
  {
    label: 'Split check',
    text: 'We have $86 food, $24 drinks, and $9.60 tax. Split among 3 adults and a 10-year-old. What does each person owe?',
  },
  {
    label: 'Now / Next / Need',
    text: 'Turn this into notes: we decided to delay the launch to May, Priya owns the blog post, and the API is still blocked on the vendor.',
  },
  { label: 'List skills', text: 'What skills are available?' },
  { label: 'No skill', text: 'Why is the sky blue?' },
];

function addMessage(who, text, cls) {
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  div.textContent = who + ': ' + text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

function formatTools(toolCalls) {
  if (!toolCalls || !toolCalls.length) return '';
  return toolCalls.map((call) => {
    const name = call.name || 'tool';
    const args = call.args || {};
    const detail = args.skill_name || args.resource_name || '';
    return detail ? name + ' → ' + detail : name;
  }).join(' · ');
}

async function sendQuestion(question) {
  if (!question) return;
  addMessage('You', question, 'me');
  input.value = '';
  const pending = addMessage('Bot', '...', 'bot');
  try {
    const res = await fetch('/api/question', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, conversation_id: conversationId }),
    });
    const data = await res.json();
    pending.remove();
    if (res.ok) {
      if (data.conversation_id) conversationId = data.conversation_id;
      addMessage('Bot', data.answer, 'bot');
      const tools = formatTools(data.tool_calls);
      if (tools) addMessage('Skills', tools, 'tools');
    } else {
      addMessage('Bot', data.detail || 'Error', 'bot');
    }
  } catch (err) {
    pending.remove();
    addMessage('Bot', 'Error: ' + err, 'bot');
  }
}

ACTIONS.forEach((action) => {
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = action.label;
  button.addEventListener('click', () => sendQuestion(action.text));
  actions.appendChild(button);
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  await sendQuestion(input.value.trim());
});
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return CHAT_PAGE

@app.get("/health/live")
async def live():
    return {"status": "ok"}

@app.get("/health/ready")
async def ready():
    return {"status": "ok"}

@app.get("/health/lcs/live")
async def lcs_live(response: Response):
    try:
        async with httpx.AsyncClient() as client:
            lcs_response = await client.get(
                f"{LCS_BASE_URL}/v1/liveness",
                timeout=10.0,
            )
            response.status_code = lcs_response.status_code
            return lcs_response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LCS liveness check failed: {str(e)}")

@app.get("/health/lcs/ready")
async def lcs_ready(response: Response):
    try:
        async with httpx.AsyncClient() as client:
            lcs_response = await client.get(
                f"{LCS_BASE_URL}/v1/readiness",
                timeout=10.0,
            )
            response.status_code = lcs_response.status_code
            return lcs_response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LCS readiness check failed: {str(e)}")

@app.get("/api/models")
async def models():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LCS_BASE_URL}/v1/models",
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error 1: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error 2: {str(e)}")

@app.post("/api/question")
async def question(
    request: Question,
):

    payload = {"query": request.question}
    if request.conversation_id:
        payload["conversation_id"] = request.conversation_id

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LCS_BASE_URL}/v1/query",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "answer": data["response"],
                "conversation_id": data.get("conversation_id"),
                "tool_calls": data.get("tool_calls", []),
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error 1: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error 2: {str(e)}")

@app.api_route(
    "/api/lcs/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def lcs_proxy(path: str, request: Request):
    """Generic passthrough to any Lightspeed Core Stack (LCS) endpoint.

    Example: GET /api/lcs/v1/models -> GET {LCS_BASE_URL}/v1/models
             POST /api/lcs/v1/query -> POST {LCS_BASE_URL}/v1/query
    """
    body = await request.body()
    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length"}
    }

    try:
        async with httpx.AsyncClient() as client:
            lcs_response = await client.request(
                request.method,
                f"{LCS_BASE_URL}/{path}",
                params=request.query_params,
                content=body,
                headers=forward_headers,
                timeout=120.0,
            )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LCS proxy failed: {str(e)}")

    response_headers = {
        k: v for k, v in lcs_response.headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
    }
    return Response(
        content=lcs_response.content,
        status_code=lcs_response.status_code,
        headers=response_headers,
        media_type=lcs_response.headers.get("content-type"),
    )
