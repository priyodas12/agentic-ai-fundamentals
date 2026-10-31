"""
Part 2 - async/await basics.
Run: python 02_coroutine_basics.py
"""
import asyncio
import time


async def greet(name: str) -> str:
    await asyncio.sleep(0.5)
    return f"Hello, {name}"


async def demo_coroutine_object():
    print("\n--- 1. Calling an async function does NOT run it ---")
    coro = greet("Priyo")             # nothing runs yet
    print("type:", type(coro))        # <class 'coroutine'>
    result = await coro               # NOW it runs
    print("result:", result)


async def demo_await_is_sequential():
    print("\n--- 2. 'await' one by one = still sequential ---")
    start = time.perf_counter()
    a = await greet("A")              # waits 0.5 s
    b = await greet("B")              # then waits another 0.5 s
    print(a, b, f"-> {time.perf_counter() - start:.2f}s (not concurrent!)")


async def demo_forgot_await():
    print("\n--- 3. Forgetting 'await' ---")
    result = greet("oops")            # BUG: no await -> result is a coroutine, not a str
    print("result is:", result)
    result.close()                    # silence the 'never awaited' warning for this demo


async def heartbeat(stop: asyncio.Event):
    """Prints a dot every 0.1 s - it stops printing if the loop is blocked."""
    while not stop.is_set():
        print(".", end="", flush=True)
        await asyncio.sleep(0.1)


async def demo_blocking_the_loop():
    print("\n--- 4. Blocking call inside async freezes EVERYTHING ---")
    stop = asyncio.Event()
    hb = asyncio.create_task(heartbeat(stop))

    await asyncio.sleep(0.3)
    print(" [bad] time.sleep(1) ", end="", flush=True)
    time.sleep(1)                     # BAD: no dots for 1 s - loop is frozen

    print(" [good] asyncio.to_thread(time.sleep, 1) ", end="", flush=True)
    await asyncio.to_thread(time.sleep, 1)   # GOOD: runs in a worker thread, dots continue

    stop.set()
    await hb
    print()


async def main():
    await demo_coroutine_object()
    await demo_await_is_sequential()
    await demo_forgot_await()
    await demo_blocking_the_loop()


if __name__ == "__main__":
    asyncio.run(main())   # the ONE entry point: creates the loop, runs main(), closes the loop
