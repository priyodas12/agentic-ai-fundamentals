"""Async-generator patterns for incremental LLM output."""


async def stream_answer(client, prompt: str):
    """Yield provider-neutral text chunks from an async stream."""
    async for chunk in client.stream(prompt):
        if chunk:
            yield chunk


async def collect_stream(client, prompt: str) -> str:
    """Display chunks as they arrive and return the complete answer."""
    parts: list[str] = []
    async for chunk in stream_answer(client, prompt):
        print(chunk, end="", flush=True)
        parts.append(chunk)
    print()
    return "".join(parts)
