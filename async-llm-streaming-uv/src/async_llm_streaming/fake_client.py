"""A fake async client so the examples run without an API key."""

import asyncio


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.output_text = text


class FakeLLMClient:
    """Simulates latency, complete responses, and streamed text chunks."""

    async def complete(self, prompt: str) -> FakeResponse:
        await asyncio.sleep(0.05)
        return FakeResponse(f"Completed answer for: {prompt}")

    async def stream(self, prompt: str):
        words = f"Streamed answer for: {prompt}".split()
        for index, word in enumerate(words):
            await asyncio.sleep(0.02)
            suffix = " " if index < len(words) - 1 else ""
            yield word + suffix
