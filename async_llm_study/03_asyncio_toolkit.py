"""
Part 3 - The asyncio toolkit (Python 3.11+).
Run: python 03_asyncio_toolkit.py
"""
import asyncio
import time


async def job(name: str, seconds: float, fail: bool = False) -> str:
    await asyncio.sleep(seconds)
    if fail:
        raise ValueError(f"{name} failed")
    return f"{name} done in {seconds}s"


def clock(start):
    return f"{time.perf_counter() - start:.2f}s"


async def demo_create_task():
    print("\n--- 1. create_task: start now, await later ---")
    start = time.perf_counter()
    t1 = asyncio.create_task(job("A", 1))   # starts running at the next await
    t2 = asyncio.create_task(job("B", 1))
    print("both tasks started, doing other work...")
    print(await t1, "|", await t2, "| total", clock(start))   # ~1 s, not 2 s


async def demo_gather():
    print("\n--- 2. gather: run many, results in INPUT order ---")
    start = time.perf_counter()
    results = await asyncio.gather(job("slow", 1.0), job("fast", 0.2), job("mid", 0.5))
    print(results, clock(start))             # order = slow, fast, mid (input order)

    print("gather + return_exceptions=True: errors come back as values")
    results = await asyncio.gather(job("ok", 0.2), job("bad", 0.1, fail=True),
                                   return_exceptions=True)
    for r in results:
        print("  ", "ERROR:" if isinstance(r, Exception) else "OK:   ", r)


async def demo_taskgroup():
    print("\n--- 3. TaskGroup: structured concurrency, cancels siblings on error ---")
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(job("A", 0.3))
        t2 = tg.create_task(job("B", 0.6))
    # leaving the 'async with' block = all tasks are finished
    print(t1.result(), "|", t2.result(), clock(start))

    start = time.perf_counter()
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(job("long", 5))           # would take 5 s...
            tg.create_task(job("bad", 0.2, fail=True))
    except* ValueError as eg:                        # ExceptionGroup syntax
        print("caught:", [str(e) for e in eg.exceptions], "- 'long' was cancelled at", clock(start))


async def demo_as_completed():
    print("\n--- 4. as_completed: handle results in FINISH order ---")
    start = time.perf_counter()
    coros = [job("slow", 1.0), job("fast", 0.2), job("mid", 0.5)]
    for next_done in asyncio.as_completed(coros):
        print("  got:", await next_done, "at", clock(start))


async def demo_timeouts():
    print("\n--- 5. Timeouts ---")
    try:
        await asyncio.wait_for(job("slow", 2), timeout=0.5)
    except TimeoutError:
        print("wait_for: timed out after 0.5s")

    try:
        async with asyncio.timeout(0.5):             # 3.11+: a timeout for a whole block
            await job("step1", 0.3)
            await job("step2", 0.3)                  # total 0.6 s > 0.5 s
    except TimeoutError:
        print("asyncio.timeout: block took too long")


async def demo_cancel():
    print("\n--- 6. Cancellation ---")

    async def worker():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            print("  worker: got CancelledError, cleaning up...")
            raise                                    # always re-raise!

    task = asyncio.create_task(worker())
    await asyncio.sleep(0.2)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("  main: task is cancelled:", task.cancelled())


async def main():
    await demo_create_task()
    await demo_gather()
    await demo_taskgroup()
    await demo_as_completed()
    await demo_timeouts()
    await demo_cancel()


if __name__ == "__main__":
    asyncio.run(main())
