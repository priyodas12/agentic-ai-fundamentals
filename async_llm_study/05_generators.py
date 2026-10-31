"""
Part 5 - Generators and async generators.
Run: python 05_generators.py
"""
import asyncio
import sys


# ---------------------------------------------------------------- 1. Normal function vs generator
def squares_list(n):
    return [i * i for i in range(n)]      # builds the WHOLE list in memory first


def squares_gen(n):
    for i in range(n):
        print(f"    (computing {i})")
        yield i * i                       # hand back ONE value, pause here


def demo_generator_basics():
    print("\n--- 1. A generator is lazy: work happens only when you ask ---")
    gen = squares_gen(3)                  # nothing printed yet - body has not started
    print("created:", gen)
    print("next ->", next(gen))           # runs until the first yield
    print("next ->", next(gen))           # resumes after yield, runs to the next one
    print("rest ->", list(gen))           # drains the remaining values
    # next(gen) now would raise StopIteration

    print("\n--- 2. Memory: list vs generator for 1,000,000 items ---")
    print("list size     :", sys.getsizeof(squares_list(1_000_000)), "bytes")
    print("generator size:", sys.getsizeof((i * i for i in range(1_000_000))), "bytes")


# ---------------------------------------------------------------- 3. Pipelines
def read_lines():
    for line in ["ERROR db down", "INFO ok", "ERROR timeout", "INFO ok"]:
        yield line


def only_errors(lines):
    for line in lines:
        if line.startswith("ERROR"):
            yield line


def demo_pipeline():
    print("\n--- 3. Generator pipeline: each stage pulls one item at a time ---")
    for line in only_errors(read_lines()):
        print("  ", line)


# ---------------------------------------------------------------- 4. Async generator
async def ticker(n, delay=0.2):
    """async def + yield = ASYNC GENERATOR. It can await between values."""
    for i in range(n):
        await asyncio.sleep(delay)        # e.g. wait for the next network chunk
        yield i


async def demo_async_generator():
    print("\n--- 4. Async generator + 'async for' ---")
    async for value in ticker(3):
        print("   tick", value)

    print("\n--- 5. Async comprehension ---")
    evens = [v async for v in ticker(6, 0.05) if v % 2 == 0]
    print("   evens:", evens)


# ---------------------------------------------------------------- 6. Transform a stream
async def upper(stream):
    """Async generators chain like normal ones: take a stream, yield a new one."""
    async for item in stream:
        yield str(item).upper()


async def words():
    for w in ["hello", "async", "world"]:
        await asyncio.sleep(0.1)
        yield w


async def demo_chain():
    print("\n--- 6. Chaining async generators ---")
    async for w in upper(words()):
        print("  ", w)


# ---------------------------------------------------------------- 7. Cleanup with aclose()
async def stream_with_cleanup():
    try:
        for i in range(100):
            await asyncio.sleep(0.05)
            yield i
    finally:
        print("   cleanup ran (e.g. close the HTTP connection)")


async def demo_early_exit():
    print("\n--- 7. Stopping early: close the generator so 'finally' runs ---")
    gen = stream_with_cleanup()
    try:
        async for i in gen:
            if i == 2:
                print("   got enough, breaking")
                break
    finally:
        await gen.aclose()                # guarantees cleanup right now


async def main():
    await demo_async_generator()
    await demo_chain()
    await demo_early_exit()


if __name__ == "__main__":
    demo_generator_basics()
    demo_pipeline()
    asyncio.run(main())
