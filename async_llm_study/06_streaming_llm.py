"""
Part 6 - Streaming LLM responses.

  1. Consume one stream, print tokens as they arrive, measure TTFT
  2. Idle timeout: give up if no token arrives for N seconds
  3. Many streams in parallel, merged into ONE output via asyncio.Queue
  4. Many streams in parallel, each collected to full text (gather)

Run: python 06_streaming_llm.py
"""
import asyncio
import time

from fake_llm import FakeLLM


# ---------------------------------------------------------------- 1. One stream
async def demo_single_stream():
    print("\n--- 1. One stream, token by token ---")
    llm = FakeLLM(seed=1)
    start = time.perf_counter()
    first_token_at = None
    parts = []

    async for token in llm.stream("What is asyncio?"):
        if first_token_at is None:
            first_token_at = time.perf_counter() - start     # TTFT
        print(token, end="", flush=True)                     # show it right away
        parts.append(token)                                  # and keep it

    full_text = "".join(parts)
    total = time.perf_counter() - start
    print(f"\n  TTFT = {first_token_at:.2f}s, total = {total:.2f}s, {len(full_text)} chars")


# ---------------------------------------------------------------- 2. Idle timeout
async def slow_stream():
    yield "fast "
    await asyncio.sleep(3)          # the server stalls
    yield "never seen"


async def with_idle_timeout(stream, seconds):
    """Wrap any async generator: raise TimeoutError if the gap between tokens > seconds."""
    it = aiter(stream)
    while True:
        try:
            async with asyncio.timeout(seconds):
                token = await anext(it)
        except StopAsyncIteration:
            return
        yield token


async def demo_idle_timeout():
    print("\n--- 2. Idle timeout between tokens ---")
    try:
        async for token in with_idle_timeout(slow_stream(), seconds=1.0):
            print("  got:", token)
    except TimeoutError:
        print("  no token for 1.0s -> gave up")


# ---------------------------------------------------------------- 3. Merge many streams
DONE = object()   # sentinel: 'this stream has finished'


async def pump(llm, stream_id, prompt, queue):
    """Read one stream and push every token into the shared queue."""
    try:
        async for token in llm.stream(prompt):
            await queue.put((stream_id, token))
    finally:
        await queue.put((stream_id, DONE))


async def demo_merged_streams():
    print("\n--- 3. Three streams at once, merged into one queue ---")
    llm = FakeLLM(seed=5)
    prompts = {"A": "Python", "B": "Java", "C": "Rust"}
    queue: asyncio.Queue = asyncio.Queue()
    texts = {sid: [] for sid in prompts}
    start = time.perf_counter()

    async with asyncio.TaskGroup() as tg:
        for sid, prompt in prompts.items():
            tg.create_task(pump(llm, sid, prompt, queue))

        remaining = len(prompts)
        while remaining:                             # consumer runs inside the group
            sid, token = await queue.get()
            if token is DONE:
                remaining -= 1
                print(f"  [{sid}] finished at {time.perf_counter()-start:.2f}s")
                continue
            texts[sid].append(token)
            print(f"  [{sid}] {token}")

    print("  final texts:")
    for sid, parts in texts.items():
        print(f"   {sid}: {''.join(parts)}")


# ---------------------------------------------------------------- 4. Collect many streams
async def collect(llm, prompt):
    return "".join([tok async for tok in llm.stream(prompt)])


async def demo_collect_many():
    print("\n--- 4. Ten streams in parallel, each collected to full text ---")
    llm = FakeLLM(seed=9)
    sem = asyncio.Semaphore(5)

    async def limited(p):
        async with sem:
            return await collect(llm, p)

    start = time.perf_counter()
    texts = await asyncio.gather(*(limited(f"topic {i}") for i in range(10)))
    print(f"  {len(texts)} full answers in {time.perf_counter()-start:.2f}s "
          f"(one by one would take ~12s)")
    print("  first:", texts[0])


async def main():
    await demo_single_stream()
    await demo_idle_timeout()
    await demo_merged_streams()
    await demo_collect_many()


if __name__ == "__main__":
    asyncio.run(main())
