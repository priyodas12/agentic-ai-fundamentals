# python-nlp-101

Hands-on NLP examples (text preprocessing, spaCy, etc.) as Jupyter notebooks under `src/`.

Environment is managed with **conda**. All dependencies live under the `conda-101` env; `requirements.txt` is the single source of truth for its pip-installed packages.

## Setup

### 1. Create the environment

```bash
conda create -n conda-101 python=3.13
```

Skip this if `conda-101` already exists (`conda env list`).

### 2. Activate it

```bash
conda activate conda-101
```

Run this in every new terminal session before working on the project. Your prompt should show `(conda-101)`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Installs `spacy`, `langchain`, the `en_core_web_sm` language model, and the rest of the stack. Takes a few minutes on first run.

### 4. Register it as a Jupyter kernel

Once per machine:

```bash
python -m ipykernel install --name conda-101 --display-name "Python (conda-101)"
```

### 5. Point PyCharm at it

**Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter → Select existing**, then paste:

```
~/anaconda3/envs/conda-101/bin/python
```

Choose **Select existing**, not "Generate new" — the latter builds a second, empty environment alongside this one.

### 6. Run the notebooks

```bash
jupyter notebook src/
```

Select the **Python (conda-101)** kernel from the kernel menu.

## Verifying the setup

```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print(nlp('It works.').text)"
```

If this prints without errors, you're ready.

## Notebooks: Text Preprocessing in NLP

The `src/` directory contains 8 hands-on notebooks covering the **NLP preprocessing pipeline**. Each notebook has simple, runnable examples.

### 1. Case Folding (`_01_case_folding.ipynb`)
Convert text to lowercase so "Hello", "HELLO", "hello" are treated as the same word.
- Reduces vocabulary size
- Improves matching and consistency
- Use `.lower()` or `.casefold()` (for multilingual text)

**Example:** `"HELLO world"` → `"hello world"`

### 2. Special Character Removal (`_02_special_character_removal.ipynb`)
Remove punctuation and symbols: `! @ # $ % & ? .`
- Collapses variants: `"Hello!"` and `"Hello?"` both become `"Hello"`
- Reduces noise in text
- Use regex: `re.sub(r"[^a-zA-Z0-9\s]", "", text)`

**Example:** `"Hello, World!"` → `"Hello World"`

### 3. Contractions Handling (`_03_contractions_handling.ipynb`)
Expand shortened words: `"can't"` → `"cannot"`, `"don't"` → `"do not"`
- Normalises different spellings of the same word
- Do this **before tokenization**
- Use `contractions.fix(text)`

**Example:** `"I can't believe it"` → `"I cannot believe it"`

### 4. Tokenization (`_04_tokenization.ipynb`)
Split text into individual tokens (words, punctuation, sentences).
- `word_tokenize()`: splits into words + punctuation
- `sent_tokenize()`: splits into sentences
- Better than `.split()` — handles punctuation correctly

**Example:** `"Dr. Smith's clinic."` → `['Dr.', 'Smith', "'s", 'clinic', '.']`

### 5. Stop Word Removal (`_05_stop_word_removal.ipynb`)
Remove common words that add little meaning: `the, is, a, and, or, it, to, in, of`
- Reduces text size
- Improves signal-to-noise ratio
- **Don't use for:** sentiment analysis, translation (loses negation like "not")
- Use `stopwords.words('english')` from NLTK

**Example:** `"The dog is running"` → `['dog', 'running']`

### 6. N-Grams (`_06_n_grams.ipynb`)
Create sequences of N words to capture context and patterns.
- **Unigrams (1-gram):** single words `["I", "love", "Python"]`
- **Bigrams (2-gram):** word pairs `[("I", "love"), ("love", "Python")]`
- **Trigrams (3-gram):** word triplets `[("I", "love", "Python")]`
- More useful for autocomplete, next-word prediction, language models

**Example:** `"I love Python"` → bigrams: `[("I", "love"), ("love", "Python")]`

### 7. Lemmatization (`_07_lemmatization.ipynb`)
Reduce a word to its dictionary base form (its "lemma") using vocabulary and grammar rules.
- Needs the part of speech (noun, verb, adjective...) to work correctly
- Unlike stemming, the output is always a real word
- Use `WordNetLemmatizer().lemmatize(word, pos=...)` from NLTK

**Example:** `"studies"` (verb) → `"study"`

### 8. Stemming (`_08_stemming.ipynb`)
Chop a word down to a root form using fixed suffix-stripping rules — fast, but the result isn't always a real word.
- Porter, Lancaster, and Snowball stemmers give different, sometimes inconsistent results
- Faster than lemmatization but less accurate
- Use `PorterStemmer().stem(word)` from NLTK

**Example:** `"studies"` → `"studi"`

---

## Typical Preprocessing Pipeline

```
Raw text
  ↓
1. Case folding (lowercase)
  ↓
2. Remove special characters
  ↓
3. Expand contractions
  ↓
4. Tokenization (split into words)
  ↓
5. Remove stop words (optional)
  ↓
6. Lemmatization (reduce to base form)
  ↓
7. N-grams or further processing
```

**Run all notebooks in order** — each step builds on the previous one. Start with `_01_case_folding.ipynb` and work through `_08_stemming.ipynb`.

## Adding a package

Add it to `requirements.txt`, then sync the environment to match it:

```bash
conda activate conda-101
pip install -r requirements.txt
```

Editing the file rather than running a bare `pip install` is what keeps the environment reproducible. A package installed ad hoc works on your machine and nowhere else.

To pin a version, write `package==1.2.3`.

> After installing anything, **restart the Jupyter kernel** — a running kernel won't see packages that appeared after it started.

## Syncing after someone else's change

When `requirements.txt` changes upstream:

```bash
conda activate conda-101
pip install -r requirements.txt
```

## Removing the environment

```bash
conda deactivate
conda env remove -n conda-101
jupyter kernelspec remove conda-101
```

The second command clears the Jupyter kernel entry. Skipping it leaves a dead kernel that fails to start when selected.
