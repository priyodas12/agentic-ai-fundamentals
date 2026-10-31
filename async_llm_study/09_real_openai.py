"""
Part 7b - The same patterns with the real OpenAI SDK (Responses API).

Install : pip install openai
Key     : export OPENAI_API_KEY=...
Model   : export OPENAI_MODEL=...   (optional; default below is the one in the SDK README -
                                     check https://platform.openai.com/docs/models)
Run     : python 09_real_openai.py
"""
import asyncio
import os
import random
import time

import openai
from openai import AsyncOpenAI

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.5")

# ONE client for the whole program. max_retries=0 because we retry ourselves.
client = AsyncOpenAI(max_retries=0, timeout=60.0)

RETRYABLE = (openai.RateLimitError, openai.InternalServerError, openai.APIConnectionError)


# ---------------------------------------------------------------- one call
async def ask(prompt: str) -> str:
    response = await client.responses.create(model=MODEL, input=prompt)
    return response.output_text


def retry_after_seconds(error) -> float | None:
    response = getattr(error, "response", None)
    if response is None:
        return None
    try:
        return float(response.headers.get("retry-after"))
    except (TypeError, ValueError):
        return None


async def ask_with_retry(prompt: str, max_attempts: int = 4) -> str:
    for attempt in range(1, max_attempts + 1):
        try:
            return await ask(prompt)
        except RETRYABLE as e:
            if attempt == max_attempts:
                raise
            delay = retry_after_seconds(e) or (0.5 * 2 ** (attempt - 1) + random.uniform(0, 0.25))
            print(f"  retry {attempt} after {type(e).__name__}, sleeping {delay:.2f}s")
            await asyncio.sleep(delay)


# ---------------------------------------------------------------- many calls in parallel
async def parallel_demo(prompts: list[str], concurrency: int = 5):
    print(f"\n--- {len(prompts)} calls, at most {concurrency} in flight ---")
    sem = asyncio.Semaphore(concurrency)

    async def one(prompt):
        async with sem:
            return await ask_with_retry(prompt)

    start = time.perf_counter()
    results = await asyncio.gather(*(one(p) for p in prompts), return_exceptions=True)
    for prompt, result in zip(prompts, results):
        status = f"ERROR {type(result).__name__}" if isinstance(result, Exception) else result[:70]
        print(f"  {prompt!r:40} -> {status}")
    print(f"  total {time.perf_counter() - start:.2f}s")


# ---------------------------------------------------------------- streaming (Responses API)
async def stream_text(prompt: str):
    """Turn the SDK's event stream into a plain async generator of text pieces."""
    stream = await client.responses.create(model=MODEL, input=prompt, stream=True)
    async for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta
        elif event.type == "error":
            raise RuntimeError(f"stream error: {event}")


async def stream_demo(prompt: str):
    print("\n--- streaming one answer ---")
    start = time.perf_counter()
    ttft = None
    parts = []
    async for text in stream_text(prompt):
        if ttft is None:
            ttft = time.perf_counter() - start
        print(text, end="", flush=True)
        parts.append(text)
    print(f"\n  TTFT {ttft:.2f}s, total {time.perf_counter() - start:.2f}s, {len(''.join(parts))} chars")

    # Chat Completions API version of the same thing (older API, still widely used):
    # stream = await client.chat.completions.create(
    #     model=MODEL, messages=[{"role": "user", "content": prompt}], stream=True)
    # async for chunk in stream:
    #     if chunk.choices and chunk.choices[0].delta.content:
    #         print(chunk.choices[0].delta.content, end="")


# ---------------------------------------------------------------- many streams merged
DONE = object()


async def pump(sid: str, prompt: str, queue: asyncio.Queue):
    try:
        async for text in stream_text(prompt):
            await queue.put((sid, text))
    finally:
        await queue.put((sid, DONE))


async def merged_streams_demo(prompts: dict[str, str]):
    print("\n--- several streams at once, merged ---")
    queue: asyncio.Queue = asyncio.Queue()
    texts = {sid: [] for sid in prompts}
    async with asyncio.TaskGroup() as tg:
        for sid, prompt in prompts.items():
            tg.create_task(pump(sid, prompt, queue))
        remaining = len(prompts)
        while remaining:
            sid, text = await queue.get()
            if text is DONE:
                remaining -= 1
            else:
                texts[sid].append(text)
    for sid, parts in texts.items():
        print(f"  [{sid}] {''.join(parts).strip()}")


async def main():
    await parallel_demo([f"In one sentence, what is {t}?" for t in
                         ["asyncio", "a coroutine", "a semaphore", "backpressure",
                          "an event loop", "a generator", "SSE", "jitter"]])
    await stream_demo("Explain Python async generators in three short sentences.")
    await merged_streams_demo({"py": "One sentence on Python.",
                               "go": "One sentence on Go.",
                               "rs": "One sentence on Rust."})


if __name__ == "__main__":
    asyncio.run(main())
