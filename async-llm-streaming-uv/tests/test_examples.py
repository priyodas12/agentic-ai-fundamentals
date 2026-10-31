import asyncio

import pytest

from async_llm_streaming.concurrency import run_many
from async_llm_streaming.fake_client import FakeLLMClient
from async_llm_streaming.streaming import stream_answer


def test_run_many_preserves_input_order() -> None:
    client = FakeLLMClient()
    prompts = ["first", "second", "third"]

    results = asyncio.run(run_many(client, prompts, max_concurrency=2))

    assert results == [
        "Completed answer for: first",
        "Completed answer for: second",
        "Completed answer for: third",
    ]


def test_run_many_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError):
        asyncio.run(run_many(FakeLLMClient(), ["prompt"], max_concurrency=0))


def test_async_stream_can_be_collected() -> None:
    async def collect() -> str:
        chunks = [chunk async for chunk in stream_answer(FakeLLMClient(), "hello")]
        return "".join(chunks)

    assert asyncio.run(collect()) == "Streamed answer for: hello"
