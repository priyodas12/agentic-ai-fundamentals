# Async LLM Streaming Study Project

A small, dependency-free `uv` project for learning:

- `async` / `await` and the asyncio event loop;
- running many independent LLM-like calls concurrently;
- limiting concurrency and handling errors;
- normal generators and async generators;
- streaming response chunks as they arrive.

The project uses a fake LLM client so it runs without an API key. Replace the fake client with your provider's async SDK when you are ready.

## Requirements

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/)

## Quick start

```bash
uv sync
uv run async-llm-demo
```

Run the tests:

```bash
uv run pytest
```

## Project layout

```text
.
├── README.md
├── pyproject.toml
├── docs/
│   └── async-llm-streaming-study-guide.md
├── src/async_llm_streaming/
│   ├── __init__.py
│   ├── concurrency.py
│   ├── fake_client.py
│   ├── streaming.py
│   └── demo.py
└── tests/
    └── test_examples.py
```

## What to explore

### Parallel calls

`concurrency.py` shows how to use `asyncio.gather()` while keeping a semaphore limit:

```python
results = await run_many(client, prompts, max_concurrency=3)
```

Results retain input order, even if individual calls finish in a different order.

### Async streaming

`streaming.py` exposes an async generator:

```python
async for chunk in stream_answer(client, prompt):
    print(chunk, end="", flush=True)
```

An async generator can pause for network I/O and yield partial output incrementally.

### Adapting to a real LLM SDK

Replace the fake client's methods with your provider's async methods. Keep the surrounding patterns:

1. use an async-compatible client;
2. put independent calls behind `asyncio.gather()`;
3. use `asyncio.Semaphore` to respect rate limits;
4. add timeouts and selective retries;
5. adapt provider-specific stream events into plain text chunks.

## Study guide

Read [`docs/async-llm-streaming-study-guide.md`](docs/async-llm-streaming-study-guide.md) for explanations, examples, a mini-project, and knowledge-check questions.
