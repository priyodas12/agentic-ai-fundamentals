"""
Part 6b - Stream LLM tokens to a browser with SSE (Server-Sent Events).

Install : pip install fastapi uvicorn
Run     : python 07_sse_server.py
Open    : http://localhost:5050          (page that shows tokens as they arrive)
Or curl : curl -N "http://localhost:5050/stream?prompt=hello"
"""
import asyncio
import json

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse

from fake_llm import FakeLLM

app = FastAPI()
llm = FakeLLM()            # one shared client for the whole app


async def sse_events(prompt: str):
    """Async generator -> each yield is one SSE message: 'data: ...\\n\\n'."""
    try:
        async for token in llm.stream(prompt):
            # json.dumps keeps newlines/quotes in the token safe inside one SSE line
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "event: done\ndata: {}\n\n"
    except asyncio.CancelledError:
        # the browser closed the tab -> the server cancels this generator
        print("client disconnected, stopping the LLM stream")
        raise


@app.get("/stream")
async def stream(prompt: str = "What is asyncio?"):
    return StreamingResponse(
        sse_events(prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # no proxy buffering
    )


PAGE = """<!doctype html>
<meta charset="utf-8"><title>SSE demo</title>
<body style="font-family:sans-serif;max-width:640px;margin:40px auto">
<input id="q" value="Explain async generators" style="width:70%">
<button onclick="go()">Ask</button>
<p id="out" style="white-space:pre-wrap;border:1px solid #ccc;padding:12px;min-height:3em"></p>
<script>
function go() {
  const out = document.getElementById('out');
  out.textContent = '';
  const es = new EventSource('/stream?prompt=' + encodeURIComponent(q.value));
  es.onmessage = (e) => { out.textContent += JSON.parse(e.data).token; };
  es.addEventListener('done', () => es.close());   // stop the browser from reconnecting
  es.onerror = () => es.close();
}
</script>
</body>"""


@app.get("/")
async def index():
    return HTMLResponse(PAGE)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)
