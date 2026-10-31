# async/await, asyncio & parallel LLM calls - runnable examples

Needs Python 3.11+. Files 01-06 and 10 run offline with a fake LLM (no API key).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # only needed for 07, 08, 09
python 01_sync_vs_async.py
```

| File | Topic |
|---|---|
| fake_llm.py | Shared fake LLM (random delay, random 429/503 errors, token streaming) |
| 01_sync_vs_async.py | Sequential vs concurrent waits, CPU work gets no speed-up |
| 02_coroutine_basics.py | Coroutine objects, await, forgotten await, blocking the loop |
| 03_asyncio_toolkit.py | create_task, gather, TaskGroup, as_completed, timeouts, cancellation |
| 04_parallel_llm_calls.py | Semaphore, retry + backoff + jitter, timeouts, progress, worker pool |
| 05_generators.py | Generators, async generators, async for, async comprehensions, aclose |
| 06_streaming_llm.py | Token streaming, TTFT, idle timeout, merging many streams |
| 07_sse_server.py | FastAPI SSE server on http://localhost:5050 |
| 08_real_anthropic.py | Same patterns with AsyncAnthropic (needs ANTHROPIC_API_KEY) |
| 09_real_openai.py | Same patterns with AsyncOpenAI Responses API (needs OPENAI_API_KEY) |
| 10_exercise_solutions.py | Solutions to the practice exercises |

Model names for 08/09 can be set with ANTHROPIC_MODEL / OPENAI_MODEL.
