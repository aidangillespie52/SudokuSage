# CSC5240-Project

# Running `app:app` with Uvicorn

This guide shows two ways to run your FastAPI app:

- **Option A (recommended):** Using [`uv`](https://github.com/astral-sh/uv)
- **Option B:** Using plain Python + `pip`

In both cases, you’ll keep your `OPENAI_API_KEY` in a `.env` file at the **project root**.

---

## 1. Project Layout (example)

You don’t need this exact structure, but this is the idea:

```bash
CSC-5240-Project/
├─ app.py          # contains FastAPI instance "app"
├─ pyproject.toml  # (if using uv)
├─ .env            # environment variables (not committed)
└─ ...
```
Your app.py should expose a FastAPI instance named app, e.g.:
```python
# app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}
```
## 2. Create `.env` with OPENAI_API_KEY
At the project root, create a file named `.env`:
```
# from CSC-5240-Project/
echo "OPENAI_API_KEY=sk-your-real-api-key-here" > .env
```
Or edit `.env` manually so it contains:
```
OPENAI_API_KEY=sk-your-real-api-key-here
```
---
## Option A - Using `uv` (recommended)
### 1. Install `uv` (one-time)
Follow the offical instructions at
`https://docs.astral.sh/uv/getting-started/installation/`
### 2. Initialize the project (if you don’t have pyproject.toml yet)
From your project directory:
```
cd CSC-5240-Project
uv init .
```
This will create a `pyproject.toml`.
### 3. Add dependencies
From inside `CSC-5240-Project`:
```
uv sync
```
This will add all of the packages necessary into a local venv.
### 4. Run the app with `uvicorn`
Still in `CSC-5240-Project`:
```
uv run uvicorn app:app --reload
```
- `app:app` = `module_name:FastAPI_instance_name`
- `-- reload` = auto-reload on code changes (dev only)

Then open:
`http://127.0.0.1:8000/`

---
## Option B — Using plain Python + pip (no uv)
### 1. Create & activate a virtual environment
From your project directory:
```
cd CSC-5240-Project
python -m venv .venv
```
### 2. Activate it:
```
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\.venv\Scripts\activate.bat

# macOS/Linux (bash or zsh)
source .venv/bin/activate

```
### 3. Install dependencies
```
pip install -r requirements.txt
```
### 4. Run it
```
python -m uvicorn app:app --reload
```