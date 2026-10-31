"""Concurrent request patterns with a bounded number of in-flight calls."""

import asyncio
from collections.abc import Sequence


async def run_many(client, prompts: Sequence[str], max_concurrency: int = 3) -> list[str]:
    """Complete prompts concurrently while respecting a concurrency limit."""
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be at least 1")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def complete_one(prompt: str) -> str:
        async with semaphore:
            response = await client.complete(prompt)
            return response.output_text

    return await asyncio.gather(*(complete_one(prompt) for prompt in prompts))
