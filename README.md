# CSC5240-Project

# Running `app:app` with Uvicorn

This guide shows two ways to run your FastAPI app:

- **Option A (recommended):** Using [`uv`](https://github.com/astral-sh/uv)
- **Option B:** Using plain Python + `pip`

In both cases, you’ll keep your `OPENAI_API_KEY` in a `.env` file at the **project root**.

---

## 1. Project Layout

This is the current project structure:

```bash
CSC-5240-Project/
├─ app.py          # contains FastAPI instance "app"
├─ pyproject.toml
├─ .env
└─ ...
```

## 2. Create `.env` with OPENAI_API_KEY
At the project root, create a file named `.env`:
Or edit `.env` manually so it contains:
```
OPENAI_API_KEY=sk-your-real-api-key-here
OPENAI_MODEL=your-desired-openai-model
```

### Available models
You can see all available OpenAI models at:
[https://platform.openai.com/docs/models](https://platform.openai.com/docs/models)

### API Key
You can generate an API Key from the OpenAI dashboard at:
[https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

### Optional:
You can add the parameter
```
INCLUDE_SOLVED_BOARD_IN_PROMPT=true
```
As a boolean if you'd like to see how the model does without
also being provided the solved solution.
---
## Option A - Using `uv` (recommended)
### 1. Install `uv` (one-time)
Follow the offical instructions at
`https://docs.astral.sh/uv/getting-started/installation/`

### 2. Add dependencies
From inside `CSC-5240-Project/`:
```
uv sync
```
This will add all of the packages necessary into a local venv.
### 3. Run the app with `uvicorn`
Still in `CSC-5240-Project/`:
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
Then open:
`http://127.0.0.1:8000/`