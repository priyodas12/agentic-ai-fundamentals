"""
Part 7a - The same patterns with the real Anthropic SDK.

Install : pip install anthropic
Key     : export ANTHROPIC_API_KEY=...
Model   : export ANTHROPIC_MODEL=...   (optional; default below is the one in the SDK README -
                                        check https://docs.claude.com/en/docs/about-claude/models)
Run     : python 08_real_anthropic.py
"""
import asyncio
import os
import random
import time

import anthropic
from anthropic import AsyncAnthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")

# ONE client for the whole program (it holds the HTTP connection pool).
# max_retries=0 because we write our own retry loop below.
# (Or delete ask_with_retry and use the SDK's built-in retries: AsyncAnthropic(max_retries=5).)
client = AsyncAnthropic(max_retries=0, timeout=60.0)

# APITimeoutError is a subclass of APIConnectionError, so it is covered too.
RETRYABLE = (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError)


# ---------------------------------------------------------------- one call
async def ask(prompt: str) -> str:
    message = await client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def retry_after_seconds(error) -> float | None:
    """Read the Retry-After header from a 429/5xx response, if the server sent one."""
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


# ---------------------------------------------------------------- streaming
async def stream_demo(prompt: str):
    print("\n--- streaming one answer ---")
    start = time.perf_counter()
    ttft = None
    # 'async with' closes the HTTP connection even if we break out early
    async with client.messages.stream(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:          # an async iterator of text pieces
            if ttft is None:
                ttft = time.perf_counter() - start
            print(text, end="", flush=True)
        final = await stream.get_final_message()       # full message + token usage
    print(f"\n  TTFT {ttft:.2f}s, total {time.perf_counter() - start:.2f}s, "
          f"tokens in/out = {final.usage.input_tokens}/{final.usage.output_tokens}")


# ---------------------------------------------------------------- many streams merged
DONE = object()


async def pump(sid: str, prompt: str, queue: asyncio.Queue):
    try:
        async with client.messages.stream(
            model=MODEL, max_tokens=200, messages=[{"role": "user", "content": prompt}]
        ) as stream:
            async for text in stream.text_stream:
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
