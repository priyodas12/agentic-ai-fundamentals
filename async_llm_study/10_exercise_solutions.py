"""
Solutions to the practice exercises. Try them yourself first!
Run: python 10_exercise_solutions.py
"""
import asyncio
import time

from fake_llm import FakeLLM


# ---------------------------------------------------------------- Ex 1: warm-up
async def ex1():
    llm = FakeLLM(seed=1)
    start = time.perf_counter()
    answers = await asyncio.gather(*(llm.complete(p) for p in ["a", "b", "c"]))
    print(f"Ex1: {answers} in {time.perf_counter()-start:.2f}s (must be < 1.6s)")


# ---------------------------------------------------------------- Ex 2: fastest model wins
async def ex2():
    models = {"model-A": FakeLLM(seed=11), "model-B": FakeLLM(seed=22), "model-C": FakeLLM(seed=33)}
    tasks = {asyncio.create_task(llm.complete("hi")): name for name, llm in models.items()}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()                                   # stop paying for the slow ones
    await asyncio.gather(*pending, return_exceptions=True)   # let cancellation finish
    winner = done.pop()
    print(f"Ex2: winner = {tasks[winner]}: {winner.result()} ({len(pending)} cancelled)")


# ---------------------------------------------------------------- Ex 3: map-reduce summary
async def ex3():
    llm = FakeLLM(seed=3)
    chunks = [f"chunk {i} of the document" for i in range(8)]
    sem = asyncio.Semaphore(3)

    async def summarise(chunk):
        async with sem:
            return await llm.complete(f"summarise: {chunk}")

    start = time.perf_counter()
    partials = await asyncio.gather(*(summarise(c) for c in chunks))      # map
    final = await llm.complete("combine: " + " | ".join(p[:15] for p in partials))  # reduce
    print(f"Ex3: {len(partials)} partial summaries + 1 final in {time.perf_counter()-start:.2f}s, "
          f"max in flight = {llm.max_in_flight}")
    print("     final:", final[:60], "...")


# ---------------------------------------------------------------- Ex 4: stop word + cleanup
async def ex4():
    llm = FakeLLM(seed=4)
    gen = llm.stream("stop test")
    collected = []
    try:
        async for tok in gen:
            if tok.strip() == "answer":
                break
            collected.append(tok)
    finally:
        await gen.aclose()
    print("Ex4: text before stop word:", "".join(collected).strip())


# ---------------------------------------------------------------- Ex 5: N calls per second
class RateLimiter:
    """Allow at most `rate` calls per second by spacing call start times."""
    def __init__(self, rate: float):
        self.interval = 1.0 / rate
        self.next_time = 0.0
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:                        # one caller books a slot at a time
            now = asyncio.get_running_loop().time()
            wait = self.next_time - now
            self.next_time = max(now, self.next_time) + self.interval
        if wait > 0:
            await asyncio.sleep(wait)

    async def __aexit__(self, *exc):
        return False


async def ex5():
    llm = FakeLLM(seed=5, min_delay=0.05, max_delay=0.1)
    limiter = RateLimiter(rate=5)                    # 5 calls per second

    async def one(i):
        async with limiter:
            return await llm.complete(f"q{i}")

    start = time.perf_counter()
    await asyncio.gather(*(one(i) for i in range(20)))
    print(f"Ex5: 20 calls at 5/s took {time.perf_counter()-start:.2f}s (expect ~3.9s)")


# ---------------------------------------------------------------- Ex 6: batch deadline, keep partial text
async def ex6():
    llm = FakeLLM(seed=6)
    texts = {i: [] for i in range(4)}

    async def read(i):
        async for tok in llm.stream(f"question {i}"):
            texts[i].append(tok)

    try:
        async with asyncio.timeout(0.8):             # deadline for the WHOLE batch
            async with asyncio.TaskGroup() as tg:
                for i in texts:
                    tg.create_task(read(i))
    except TimeoutError:
        print("Ex6: deadline hit, partial answers:")
    for i, parts in texts.items():
        print(f"     [{i}] {len(parts):2} tokens: {''.join(parts)[:45]}...")


async def main():
    for ex in (ex1, ex2, ex3, ex4, ex5, ex6):
        await ex()


if __name__ == "__main__":
    asyncio.run(main())
