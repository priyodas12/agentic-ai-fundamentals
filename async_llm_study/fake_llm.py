"""
fake_llm.py - a pretend LLM client, so every example runs offline.

It behaves like a real network call:
  * each call takes a random time (0.3 - 1.5 s)
  * some calls fail at random (like HTTP 429 / 503 errors)
  * stream() yields the answer token by token
"""
import asyncio
import random


class RateLimitError(Exception):
    """Pretend HTTP 429 - 'too many requests'. Safe to retry."""


class ServerError(Exception):
    """Pretend HTTP 503 - 'server busy'. Safe to retry."""


class FakeLLM:
    def __init__(self, fail_rate: float = 0.0, min_delay=0.3, max_delay=1.5, seed=None):
        self.fail_rate = fail_rate
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.rng = random.Random(seed)
        self.in_flight = 0        # how many calls are running right now
        self.max_in_flight = 0    # highest value seen (to prove limits work)

    async def complete(self, prompt: str) -> str:
        """One full request -> one full answer (like a non-streaming API call)."""
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        try:
            # 'await' hands control back to the event loop while we "wait for the network"
            await asyncio.sleep(self.rng.uniform(self.min_delay, self.max_delay))
            if self.rng.random() < self.fail_rate:
                raise self.rng.choice([RateLimitError, ServerError])(f"failed: {prompt[:30]}")
            return f"Answer to '{prompt}'"
        finally:
            self.in_flight -= 1

    async def stream(self, prompt: str):
        """An ASYNC GENERATOR: yields the answer one token at a time."""
        await asyncio.sleep(self.rng.uniform(0.2, 0.6))        # time to first token
        words = f"Here is a short streamed answer to the question: {prompt}".split()
        for word in words:
            await asyncio.sleep(self.rng.uniform(0.03, 0.12))   # gap between tokens
            yield word + " "
