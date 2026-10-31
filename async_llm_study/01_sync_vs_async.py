"""
Part 1 - Sync vs async.
Five pretend network calls, each takes 1 second.
  Sync  : one after another  -> ~5 s
  Async : all wait together  -> ~1 s
"""
import asyncio
import time


# ---------- SYNC: time.sleep() blocks the whole thread ----------
def fetch_sync(i: int) -> str:
    time.sleep(1)                 # thread is stuck here, doing nothing
    return f"result {i}"


def run_sync():
    start = time.perf_counter()
    results = [fetch_sync(i) for i in range(5)]
    print(f"sync : {results} in {time.perf_counter() - start:.2f}s")


# ---------- ASYNC: await asyncio.sleep() gives the thread back ----------
async def fetch_async(i: int) -> str:
    await asyncio.sleep(1)        # "pause me, run someone else, wake me in 1 s"
    return f"result {i}"


async def run_async():
    start = time.perf_counter()
    results = await asyncio.gather(*(fetch_async(i) for i in range(5)))
    print(f"async: {results} in {time.perf_counter() - start:.2f}s")


# ---------- CPU-bound work does NOT get faster with async ----------
def busy(n: int) -> int:
    return sum(i * i for i in range(n))


async def cpu_in_async():
    start = time.perf_counter()
    # No 'await' inside busy() -> nothing to switch on -> runs one by one anyway
    for _ in range(3):
        busy(3_000_000)
    print(f"cpu work inside async (no speed-up): {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())
    asyncio.run(cpu_in_async())
