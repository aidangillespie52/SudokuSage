# backend/services/ai_service.py

import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from backend.utils import get_logger
from typing import List

logger = get_logger(__name__)
load_dotenv()

# configs
API_KEY = os.getenv("OPENAI_API_KEY")
URL = "https://api.openai.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

MODEL = "gpt-5-mini"

async def call_llm(session: aiohttp.ClientSession, messages: List[str]) -> str:
    payload = {
        "model": MODEL,
        "messages": messages,
    }
    
    async with session.post(URL, headers=HEADERS, json=payload, timeout=60) as resp:
        if resp.status != 200:
            raise RuntimeError(f"LLM error {resp.status}: {await resp.text()}")
        
        data = await resp.json()
        return data["choices"][0]["message"]["content"]

async def _demo():
    async with aiohttp.ClientSession() as session:
        prompt = "Explain the theory of relativity in simple terms."
        response = await call_llm(session, prompt)
        print("Response from GPT:")
        print(response)

if __name__ == "__main__":
    asyncio.run(_demo())