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
your-project/
├─ app.py          # contains FastAPI instance "app"
├─ pyproject.toml  # (if using uv)
├─ .env            # environment variables (not committed)
└─ ...
```
Your app.py should expose a FastAPI instance named app, e.g.:
```
# app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}
```