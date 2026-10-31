"""Command-line demonstration for the study project."""

import asyncio

from .concurrency import run_many
from .fake_client import FakeLLMClient
from .streaming import collect_stream


async def demo() -> None:
    client = FakeLLMClient()

    prompts = [
        "Explain async/await in one sentence",
        "Explain asyncio.gather in one sentence",
        "Explain async generators in one sentence",
    ]
    print("Concurrent completions:")
    for answer in await run_many(client, prompts, max_concurrency=2):
        print(f"- {answer}")

    print("\nStreaming response:")
    await collect_stream(client, "Why is streaming useful for chat applications?")


def main() -> None:
    asyncio.run(demo())


if __name__ == "__main__":
    main()
