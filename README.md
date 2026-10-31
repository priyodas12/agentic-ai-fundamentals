# agentic-ai-fundamentals

A personal study workspace of Python learning material, ordered as a path toward AI/agentic work. It starts with core Python and the NumPy/pandas/NLP basics, then covers async Python and parallel/streaming LLM calls. Most of it is Jupyter notebooks; the async material is runnable scripts.

## What's inside

| Folder | Topic | Format |
|---|---|---|
| `python-basics/` | Core Python: syntax, variables, data types, operators, conditionals, loops, functions, file I/O, standard library, exceptions, OOP, iterators/generators, logging (`loguru`) | 13 numbered topic folders of notebooks |
| `numpy/numpy-101/` | NumPy basics: lists vs arrays, creation, attributes, operations, indexing, loops, stacking, splitting | notebooks + `00_why_use_numpy.md` |
| `numpy/numpy-102/` | Intermediate NumPy: fancy and boolean indexing, broadcasting, sigmoid, mean squared error, plotting, tricks | notebooks |
| `numpy/numpy-pandas-study-material/numpy-pandas-study/` | 8-notebook NumPy + pandas track for Java/SQL engineers, with synthetic order data | notebooks + `data/*.csv` |
| `numpy/NumPy_Pandas_Study_Guide.pdf` | Companion study guide | PDF |
| `pandas/pandas-101/` | pandas `Series` and `DataFrame`, using Bollywood-movie and IPL batting CSVs | notebooks + `src/data/*.csv` |
| `nlp/python-nlp-101/` | Text preprocessing: case folding, special-character removal, contractions, tokenization, stop words, n-grams, lemmatization, stemming | notebooks |
| `async_llm_study/` | `async`/`await`, asyncio toolkit, parallel LLM calls (semaphore, retry/backoff, timeouts), generators, token streaming, SSE server, real Anthropic/OpenAI SDK examples | numbered `.py` scripts |
| `async-llm-streaming-uv/` | Small dependency-free `uv` package of the same async ideas, with tests and a study guide | Python package + pytest |

## Tech stack

- **Python**: 3.11+ for the async projects (`requires-python >=3.11`); the NLP project's README uses 3.13.
- **Notebooks**: Jupyter (pinned stack in `python-basics/requirements.txt`).
- **Data**: NumPy, pandas, matplotlib (optional).
- **NLP**: spaCy (`en_core_web_sm` 3.8.0), NLTK, contractions, scikit-learn, gensim, tiktoken, LangChain packages.
- **Async/LLM**: `asyncio`, FastAPI + uvicorn (SSE demo), `anthropic`, `openai` SDKs.
- **Tooling**: `uv` + hatchling + pytest (`async-llm-streaming-uv`), conda (`nlp`), pip.

## Project structure

```text
.
├── python-basics/                 # 13 topic folders (_01_syntax_semantics ... _13_python_logging)
├── numpy/
│   ├── numpy-101/src/             # beginner notebooks
│   ├── numpy-102/src/             # intermediate notebooks
│   ├── numpy-pandas-study-material/numpy-pandas-study/
│   │   ├── notebooks/             # 01-08
│   │   └── data/                  # customers, orders, order_items, daily_metrics
│   └── NumPy_Pandas_Study_Guide.pdf
├── pandas/pandas-101/src/         # series/, dataframe/, data/
├── nlp/python-nlp-101/src/        # 8 preprocessing notebooks
├── async_llm_study/               # scripts 01-10 + fake_llm.py
└── async-llm-streaming-uv/        # src/async_llm_streaming, tests, docs
```

## Setup

Each sub-project is self-contained. Pick the one you want.

### python-basics

```bash
cd python-basics
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

### NumPy / pandas study track

```bash
cd numpy/numpy-pandas-study-material/numpy-pandas-study
pip install -r requirements.txt     # numpy, pandas, jupyterlab (+ optional pyarrow, numexpr, matplotlib)
jupyter lab
```

For `numpy-101`, `numpy-102` and `pandas-101`, `pip install numpy pandas jupyter` is enough (matplotlib for the plotting notebook).

### NLP

```bash
cd nlp/python-nlp-101
conda create -n conda-101 python=3.13
conda activate conda-101
pip install -r requirements.txt
python -m ipykernel install --name conda-101 --display-name "Python (conda-101)"
jupyter notebook src/
```

Run the notebooks in order (`_01` to `_08`); the README in that folder describes each step.

### async_llm_study

```bash
cd async_llm_study
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # only needed for 07, 08, 09
```

### async-llm-streaming-uv

```bash
cd async-llm-streaming-uv
uv sync
```

## Configuration

Only the real-SDK scripts in `async_llm_study/` need credentials. Set them as environment variables; do not put values in files.

| Variable | Used by | Required |
|---|---|---|
| `ANTHROPIC_API_KEY` | `08_real_anthropic.py` | yes |
| `ANTHROPIC_MODEL` | `08_real_anthropic.py` | no (script has a default) |
| `OPENAI_API_KEY` | `09_real_openai.py` | yes |
| `OPENAI_MODEL` | `09_real_openai.py` | no (script has a default) |

`.env` files are Git-ignored by the root `.gitignore`.

## Usage

**Async scripts** (offline, use a fake LLM from `fake_llm.py`):

```bash
cd async_llm_study
python 01_sync_vs_async.py      # also 02 - 06 and 10
python 07_sse_server.py         # then open http://localhost:5050
curl -N "http://localhost:5050/stream?prompt=hello"
python 08_real_anthropic.py     # needs ANTHROPIC_API_KEY
python 09_real_openai.py        # needs OPENAI_API_KEY
```

| Script | Topic |
|---|---|
| `01_sync_vs_async.py` | Sequential vs concurrent waits |
| `02_coroutine_basics.py` | Coroutines, `await`, common mistakes |
| `03_asyncio_toolkit.py` | `create_task`, `gather`, `TaskGroup`, `as_completed`, timeouts, cancellation |
| `04_parallel_llm_calls.py` | Semaphore, retry + backoff, per-call timeout, worker pool |
| `05_generators.py` | Generators and async generators |
| `06_streaming_llm.py` | Token streaming, time to first token, merging streams |
| `07_sse_server.py` | FastAPI Server-Sent Events server |
| `08_real_anthropic.py`, `09_real_openai.py` | The same patterns with real SDKs |
| `10_exercise_solutions.py` | Practice-exercise solutions |

**uv package:**

```bash
cd async-llm-streaming-uv
uv run async-llm-demo
uv run pytest
```

Read `async-llm-streaming-uv/docs/async-llm-streaming-study-guide.md` for explanations and knowledge-check questions.

**Notebooks:** open them with `jupyter lab` (or in PyCharm/VS Code) from the relevant sub-project.

## Notes

- **Data:** `pandas/pandas-101/src/data/` holds the Bollywood movie and IPL batsman CSVs. The `numpy-pandas-study` data is synthetic, with missing values added on purpose.
- **Versions:** the NumPy/pandas study track was written against NumPy 2.4 and pandas 3.0 (Copy-on-Write always on).
- **Folder names:** some folders keep original spellings (`_06_pyhton_loops`, `_09_pyhton_standard_library`); the typos are left in place so existing paths keep working.
- **Possible requirements typos:** `nlp/python-nlp-101/requirements.txt` lists `pydentic` and `pypi`, which look like typos for `pydantic` and similar. Check before running `pip install`.
- **Sub-READMEs out of date:** `numpy/numpy-102/README.md` and `pandas/pandas-101/README.md` list fewer notebooks than the folders contain.
- **Credential scan:** `.chkcredignore` lists four files with known false positives (demo passwords and a CLI flag), so `/chk-cred` skips them.
- No root-level license or CI configuration was found.
