"""
Part 4 - Running many LLM calls in parallel, safely.

  Step 1: naive gather        -> fast, but 50 requests hit the API at once
  Step 2: Semaphore           -> at most N requests in flight
  Step 3: retry + backoff     -> survive 429 / 503 errors
  Step 4: timeout per call    -> one stuck call cannot hang the batch
  Step 5: progress + summary  -> as_completed, keep input order in the result
  Step 6: worker pool         -> for 10k+ prompts, N workers pull from a Queue

Run: python 04_parallel_llm_calls.py
"""
import asyncio
import random
import time

from fake_llm import FakeLLM, RateLimitError, ServerError

PROMPTS = [f"Summarise document #{i}" for i in range(50)]
RETRYABLE = (RateLimitError, ServerError, TimeoutError)


# ---------------------------------------------------------------- Step 1
async def step1_naive():
    llm = FakeLLM(seed=1)
    start = time.perf_counter()
    answers = await asyncio.gather(*(llm.complete(p) for p in PROMPTS))
    print(f"[1] naive gather : {len(answers)} answers in {time.perf_counter()-start:.2f}s, "
          f"max in flight = {llm.max_in_flight}  <- real APIs would return 429 here")


# ---------------------------------------------------------------- Step 2
async def step2_semaphore(limit: int = 10):
    llm = FakeLLM(seed=1)
    sem = asyncio.Semaphore(limit)          # a counter with 'limit' permits

    async def limited(prompt):
        async with sem:                     # wait for a free permit
            return await llm.complete(prompt)   # permit is returned on exit, even on error

    start = time.perf_counter()
    answers = await asyncio.gather(*(limited(p) for p in PROMPTS))
    print(f"[2] semaphore={limit}: {len(answers)} answers in {time.perf_counter()-start:.2f}s, "
          f"max in flight = {llm.max_in_flight}")


# ---------------------------------------------------------------- Step 3 + 4
async def call_with_retry(llm, prompt, *, max_attempts=4, base_delay=0.2, timeout=3.0):
    """Retry retryable errors with exponential backoff + jitter. Timeout each attempt."""
    for attempt in range(1, max_attempts + 1):
        try:
            async with asyncio.timeout(timeout):          # Step 4
                return await llm.complete(prompt)
        except RETRYABLE as e:
            if attempt == max_attempts:
                raise                                    # give up, let caller see the error
            # exponential backoff: 0.2, 0.4, 0.8 ... plus random jitter
            delay = base_delay * 2 ** (attempt - 1) + random.uniform(0, 0.1)
            print(f"    retry {attempt} for '{prompt}' after {type(e).__name__}, sleep {delay:.2f}s")
            await asyncio.sleep(delay)


# ---------------------------------------------------------------- Step 5: the full pattern
async def run_batch(prompts, *, concurrency=10, fail_rate=0.15):
    llm = FakeLLM(fail_rate=fail_rate, seed=7)
    sem = asyncio.Semaphore(concurrency)

    async def one(index, prompt):
        async with sem:
            try:
                return index, await call_with_retry(llm, prompt), None
            except Exception as e:                       # keep going, record the error
                return index, None, e

    results = [None] * len(prompts)
    errors = {}
    start = time.perf_counter()

    tasks = [one(i, p) for i, p in enumerate(prompts)]
    for done_count, next_done in enumerate(asyncio.as_completed(tasks), start=1):
        index, answer, error = await next_done
        if error:
            errors[index] = error
        else:
            results[index] = answer                      # store in INPUT order
        if done_count % 10 == 0 or done_count == len(prompts):
            print(f"  progress: {done_count}/{len(prompts)}")

    elapsed = time.perf_counter() - start
    print(f"[5] full pattern : {len(prompts)-len(errors)} ok, {len(errors)} failed, "
          f"{elapsed:.2f}s, max in flight = {llm.max_in_flight}")
    for i, e in errors.items():
        print(f"    failed #{i}: {type(e).__name__}: {e}")
    return results, errors


# ---------------------------------------------------------------- Step 6: worker pool
async def worker_pool(prompts, *, workers=10):
    """For very large jobs (10k+ prompts): N workers pull from a queue.
    Only N tasks exist at any time, instead of one task per prompt."""
    llm = FakeLLM(seed=3, min_delay=0.05, max_delay=0.15)
    queue: asyncio.Queue = asyncio.Queue()
    for item in enumerate(prompts):
        queue.put_nowait(item)
    results = [None] * len(prompts)

    async def worker():
        while True:
            try:
                index, prompt = queue.get_nowait()
            except asyncio.QueueEmpty:
                return                                   # no work left -> worker exits
            results[index] = await call_with_retry(llm, prompt)

    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        for _ in range(workers):
            tg.create_task(worker())
    print(f"[6] worker pool  : {len(prompts)} prompts, {workers} workers, "
          f"{time.perf_counter()-start:.2f}s, max in flight = {llm.max_in_flight}")
    return results


async def main():
    await step1_naive()
    await step2_semaphore(10)
    await step2_semaphore(5)
    print("[3-5] retries + timeouts + progress (15% of calls fail at random):")
    await run_batch(PROMPTS)
    await worker_pool([f"prompt {i}" for i in range(1000)], workers=20)


if __name__ == "__main__":
    random.seed(42)
    asyncio.run(main())
