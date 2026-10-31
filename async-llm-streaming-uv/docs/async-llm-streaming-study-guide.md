# Study Guide: Async Python, Parallel LLM Calls, and Streaming

## What you will learn

By the end, you should be able to:

- explain the difference between synchronous and asynchronous code;
- write and run `async` functions with `await` and `asyncio.run()`;
- run independent LLM calls concurrently with `asyncio.gather()`;
- limit concurrency, handle failures, and preserve result order;
- understand normal generators, async generators, and `yield`;
- stream an LLM response to a user as chunks arrive.

The examples use Python 3.11+ syntax and a provider-neutral `client` object. Replace the placeholder client calls with the methods from your LLM SDK.

---

## 1. The core mental model

### Synchronous code

Synchronous code waits for one operation to finish before starting the next:

```python
answer_a = call_llm("Explain photosynthesis")  # waits
answer_b = call_llm("Explain gravity")        # starts afterward
```

If each request takes two seconds, the total time is approximately four seconds.

### Asynchronous code

Asynchronous code can pause while waiting for I/O—such as a network response—and let other work run during that pause:

```python
answer_a, answer_b = await asyncio.gather(
    call_llm_async("Explain photosynthesis"),
    call_llm_async("Explain gravity"),
)
```

If both requests are independent and each takes two seconds, the total time can be close to two seconds, plus overhead.

Asyncio is most useful for I/O-bound work. It does not automatically make CPU-heavy Python code faster.

---

## 2. `async`, `await`, and the event loop

### Defining an async function

Use `async def` to define a coroutine function:

```python
import asyncio


async def fetch_topic(topic: str) -> str:
    print(f"Starting: {topic}")
    await asyncio.sleep(1)  # Simulates network I/O
    return f"Result for {topic}"
```

Calling `fetch_topic(...)` does not immediately execute it. It creates a coroutine object. The coroutine runs when it is awaited or scheduled:

```python
async def main() -> None:
    result = await fetch_topic("asyncio")
    print(result)


asyncio.run(main())
```

### What `await` means

`await operation()` means:

1. start or continue the asynchronous operation;
2. pause this coroutine until the operation has a result;
3. allow the event loop to run other ready tasks meanwhile;
4. resume this coroutine when the result is available.

You can only use `await` inside an `async def` function.

### Running tasks concurrently

`asyncio.create_task()` schedules a coroutine so it can run concurrently with the current coroutine:

```python
async def main() -> None:
    task_a = asyncio.create_task(fetch_topic("asyncio"))
    task_b = asyncio.create_task(fetch_topic("generators"))

    # Both tasks have had an opportunity to run by this point.
    result_a = await task_a
    result_b = await task_b
    print(result_a, result_b)
```

For a group of independent operations, `asyncio.gather()` is often simpler:

```python
async def main() -> None:
    results = await asyncio.gather(
        fetch_topic("asyncio"),
        fetch_topic("generators"),
        fetch_topic("LLMs"),
    )
    print(results)
```

`gather()` returns results in the same order as the awaitables you pass in, even if they finish in a different order.

### A common mistake

This is sequential, not parallel:

```python
for prompt in prompts:
    result = await call_llm_async(prompt)
    print(result)
```

This creates a group of concurrent operations:

```python
results = await asyncio.gather(
    *(call_llm_async(prompt) for prompt in prompts)
)
```

---

## 3. Running many LLM calls in parallel

Assume an async SDK method shaped like this:

```python
response = await client.responses.create(
    model="your-model",
    input=prompt,
)
text = response.output_text
```

### Basic parallel fan-out

```python
import asyncio


async def ask_llm(client, prompt: str) -> str:
    response = await client.responses.create(
        model="your-model",
        input=prompt,
    )
    return response.output_text


async def answer_many(client, prompts: list[str]) -> list[str]:
    return await asyncio.gather(
        *(ask_llm(client, prompt) for prompt in prompts)
    )
```

Use this when the calls are independent—for example, generating several candidate titles or classifying many separate documents.

### Measuring the benefit

```python
import time


async def main(client) -> None:
    prompts = [
        "Summarize document A",
        "Summarize document B",
        "Summarize document C",
    ]

    start = time.perf_counter()
    answers = await answer_many(client, prompts)
    elapsed = time.perf_counter() - start

    print(f"Completed {len(answers)} calls in {elapsed:.2f}s")


# Run from a normal Python entry point:
# asyncio.run(main(client))
```

Parallelism improves latency, but it can increase rate-limit pressure, cost, and simultaneous memory usage.

### Limiting concurrency with a semaphore

Do not launch hundreds or thousands of calls without a limit. A semaphore lets only a fixed number run at once:

```python
import asyncio


async def ask_with_limit(client, prompt: str, limit: asyncio.Semaphore) -> str:
    async with limit:
        response = await client.responses.create(
            model="your-model",
            input=prompt,
        )
        return response.output_text


async def answer_many_safely(client, prompts: list[str]) -> list[str]:
    limit = asyncio.Semaphore(5)  # At most five requests at a time.
    return await asyncio.gather(
        *(ask_with_limit(client, prompt, limit) for prompt in prompts)
    )
```

Choose the limit based on the provider's rate limits, your budget, and the desired latency. Five is only an example.

### Handling errors

By default, if one awaitable in `gather()` raises an exception, the group raises an exception too:

```python
results = await asyncio.gather(*calls, return_exceptions=True)

for prompt, result in zip(prompts, results):
    if isinstance(result, Exception):
        print(f"Failed for {prompt!r}: {result}")
    else:
        print(result)
```

For production code, also consider timeouts and retries with backoff:

```python
async def ask_with_timeout(client, prompt: str) -> str:
    async with asyncio.timeout(30):
        response = await client.responses.create(
            model="your-model",
            input=prompt,
        )
        return response.output_text
```

Retry only errors that are likely temporary, such as a timeout or rate-limit response. Avoid blindly retrying invalid requests, authentication failures, or safety-policy failures.

### When calls depend on one another

Do not parallelize dependent work:

```python
draft = await ask_llm(client, "Write a draft")
final = await ask_llm(client, f"Improve this draft: {draft}")
```

The second request needs the first result, so this sequence is correct.

---

## 4. Generators and streaming

### Normal generators

A generator produces values one at a time using `yield`:

```python
def count_up_to(limit: int):
    number = 1
    while number <= limit:
        yield number
        number += 1


for number in count_up_to(3):
    print(number)
```

Output:

```text
1
2
3
```

The generator pauses at each `yield` and resumes when the next value is requested. This avoids building the entire sequence in memory.

### Why generators are useful for LLMs

An LLM may produce a response incrementally. A streaming API can expose text chunks as they arrive:

```python
def stream_response(client, prompt: str):
    stream = client.responses.create(
        model="your-model",
        input=prompt,
        stream=True,
    )

    for event in stream:
        text = extract_text_from_event(event)
        if text:
            yield text
```

The caller can display each chunk immediately rather than waiting for the complete response.

The exact event shape differs by SDK. Treat `extract_text_from_event()` as provider-specific adapter code.

---

## 5. Async generators

An async generator uses both `async def` and `yield`:

```python
import asyncio


async def numbers_slowly():
    for number in range(3):
        await asyncio.sleep(0.5)
        yield number


async def main() -> None:
    async for number in numbers_slowly():
        print(number)


asyncio.run(main())
```

Use `async for` to consume an async generator. Use `for` for a normal generator; mixing them up causes an error.

### Async LLM streaming pattern

```python
async def stream_llm(client, prompt: str):
    stream = await client.responses.create(
        model="your-model",
        input=prompt,
        stream=True,
    )

    async for event in stream:
        text = extract_text_from_event(event)
        if text:
            yield text


async def print_stream(client, prompt: str) -> None:
    async for chunk in stream_llm(client, prompt):
        print(chunk, end="", flush=True)
    print()
```

Some SDKs return an async iterator directly; others require awaiting a method before iterating. Check the SDK's documentation and adjust the one line that creates `stream`.

### Collecting a stream

If you need the complete answer after showing it:

```python
async def consume_and_collect(client, prompt: str) -> str:
    parts: list[str] = []

    async for chunk in stream_llm(client, prompt):
        print(chunk, end="", flush=True)
        parts.append(chunk)

    print()
    return "".join(parts)
```

Streaming is about delivery timing; it does not necessarily reduce the total number of output tokens or the total cost.

---

## 6. Parallel streaming

You can stream multiple independent responses at once, but their chunks arrive interleaved. Label each stream so the consumer knows where each chunk belongs:

```python
async def print_one_stream(client, name: str, prompt: str) -> None:
    async for chunk in stream_llm(client, prompt):
        print(f"[{name}] {chunk}", flush=True)


async def stream_many(client, jobs: dict[str, str]) -> None:
    await asyncio.gather(
        *(print_one_stream(client, name, prompt)
          for name, prompt in jobs.items())
    )
```

For a web application, do not write all users' chunks to one terminal. Send each chunk to the correct client connection, queue, or UI component.

### A queue-based pattern

An `asyncio.Queue` is useful when producers and consumers should be separate:

```python
async def produce(client, prompt: str, queue: asyncio.Queue) -> None:
    async for chunk in stream_llm(client, prompt):
        await queue.put(chunk)
    await queue.put(None)  # Sentinel means "finished".


async def consume(queue: asyncio.Queue) -> None:
    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        print(chunk, end="", flush=True)
```

Queues also provide a natural place to apply backpressure: if the consumer is slow and the queue is bounded, producers wait instead of allowing memory to grow without limit.

---

## 7. Practical safety and reliability checklist

- Use an async-compatible HTTP/LLM client. Calling a blocking client inside async code can freeze the event loop.
- Put a timeout around network operations.
- Limit concurrency with a semaphore.
- Handle cancellation so abandoned requests can stop cleanly.
- Retry temporary failures with exponential backoff and a maximum retry count.
- Respect provider rate limits and token limits.
- Keep API keys in environment variables or a secret manager, never in source code.
- Validate and log metadata such as request ID, latency, model, and error type; avoid logging sensitive prompts or responses by default.
- Remember that streamed partial output may need a finalization step before it is saved or parsed as structured data.

### Cancellation example

```python
async def stream_until_cancelled(client, prompt: str) -> None:
    try:
        async for chunk in stream_llm(client, prompt):
            print(chunk, end="", flush=True)
    except asyncio.CancelledError:
        # Close provider-specific stream resources here if needed.
        print("\nStream cancelled")
        raise  # Preserve cancellation semantics.
```

---

## 8. Debugging guide

### “I forgot to await”

Symptom: you print a coroutine object or see a warning such as “coroutine was never awaited.”

```python
result = ask_llm(client, prompt)       # Wrong: coroutine object
result = await ask_llm(client, prompt) # Correct inside async def
```

### “My calls are still sequential”

Look for `await` inside a loop. Build the calls first, then await them together with `gather()`.

### “My event loop is blocked”

Look for synchronous network libraries, `time.sleep()`, or expensive CPU work inside async functions. Use an async client, `await asyncio.sleep()`, or move CPU-heavy work to a thread/process strategy.

### “The stream does not print immediately”

Use `flush=True` in terminal output and confirm that the server, proxy, and client all support streaming. Some systems buffer output even when the model is sending chunks.

### “Chunks are not complete words”

That is normal. A chunk may contain part of a word, punctuation, or several tokens. Append chunks in order; do not assume each chunk is independently valid text or JSON.

---

## 9. Mini project: concurrent summaries with streamed output

Design a function that:

1. accepts a list of documents;
2. limits concurrent requests to three;
3. streams each summary as it arrives;
4. labels output by document ID;
5. returns the complete summaries;
6. records a useful error if one document fails.

A solution outline:

```python
async def summarize_one(client, doc_id: str, text: str,
                        limit: asyncio.Semaphore) -> tuple[str, str]:
    parts: list[str] = []

    async with limit:
        async for chunk in stream_llm(
            client,
            f"Summarize document {doc_id}:\n\n{text}",
        ):
            print(f"[{doc_id}] {chunk}", end="", flush=True)
            parts.append(chunk)

    print()
    return doc_id, "".join(parts)


async def summarize_all(client, documents: dict[str, str]):
    limit = asyncio.Semaphore(3)
    jobs = [
        summarize_one(client, doc_id, text, limit)
        for doc_id, text in documents.items()
    ]
    results = await asyncio.gather(*jobs, return_exceptions=True)

    completed: dict[str, str] = {}
    errors: dict[str, str] = {}
    for doc_id, result in zip(documents, results):
        if isinstance(result, Exception):
            errors[doc_id] = str(result)
        else:
            _, summary = result
            completed[doc_id] = summary

    return completed, errors
```

This outline assumes `stream_llm()` is already adapted to your provider's event format. Add retries, timeout handling, and cancellation behavior before using it in production.

---

## 10. Knowledge check

1. What is the difference between a coroutine and a task?
2. Why does `asyncio.gather()` help with independent LLM calls?
3. Why should concurrency usually be limited?
4. What is the difference between `yield` and `return` in a generator?
5. How do you consume a normal generator versus an async generator?
6. Why might streamed chunks not form complete words?
7. What happens if one operation in `asyncio.gather()` raises an exception?
8. When should two LLM calls remain sequential?

### Short answers

1. A coroutine is awaitable work; a task schedules that coroutine on the event loop.
2. It lets the event loop make progress on several I/O-bound calls while each waits for the network.
3. To respect rate limits, control cost, avoid resource exhaustion, and reduce failures.
4. `yield` pauses a generator and produces an intermediate value; `return` ends the function.
5. Use `for` with a normal generator and `async for` with an async generator.
6. Streams commonly expose token or small text fragments rather than word boundaries.
7. By default, the gather call raises; with `return_exceptions=True`, exceptions appear in the results list.
8. When the second call needs the result of the first.

---

## 11. Quick reference

```python
async def fn():                 # Define coroutine
    result = await other()      # Wait without blocking event loop
    return result

asyncio.run(main())             # Start top-level async program
task = asyncio.create_task(fn())# Schedule concurrent work
results = await asyncio.gather(a, b)

def generate():                 # Normal generator
    yield value

async def stream():             # Async generator
    await wait_for_io()
    yield chunk

for value in generate():        # Consume normal generator
    ...

async for chunk in stream():    # Consume async generator
    ...
```

The central pattern is:

```python
async def main():
    # Start independent I/O work together.
    results = await asyncio.gather(...)

    # Deliver long-running output incrementally.
    async for chunk in stream_llm(...):
        handle(chunk)
```
