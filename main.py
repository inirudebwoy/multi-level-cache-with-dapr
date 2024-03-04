import asyncio
import base64
import hashlib
import json
import os
from functools import wraps
from typing import Any, Optional

import httpx
from fastapi import FastAPI

app = FastAPI()

base_url = (
    os.getenv("BASE_URL", "http://localhost")
    + ":"
    + os.getenv("DAPR_HTTP_PORT", "3500")
)
DAPR_STATE_STORE = "2nd-lvl-cache"


async def expensive_function(key):
    print("expensive function called")
    await asyncio.sleep(1)
    return hashlib.sha256(key.encode()).hexdigest()


async def get_from_dapr(key: str) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/v1.0/state/{DAPR_STATE_STORE}/{key}",
        )
        if response.status_code == 200:
            return response.json()


async def set_to_dapr(key: str, value: Any, ttl: int):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{base_url}/v1.0/state/{DAPR_STATE_STORE}",
            json=[{"key": key, "value": value, "metadata": {"ttlInSeconds": str(ttl)}}],
        )


def cache(ttl: int = 60):
    def _cache(f):
        _cache = {}

        @wraps(f)
        async def wrapped(*args, **kwargs):
            serialized = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
            # Hash the serialized string to ensure a consistent and short length
            hashed = hashlib.sha256(serialized.encode()).digest()
            # Encode the hash using base64 URL-safe encoding
            key = base64.urlsafe_b64encode(hashed).decode()

            if value := _cache.get(key):
                print("lvl 1 cache hit")
                return value
            if value := await get_from_dapr(key):
                print("lvl 2 cache hit")
                _cache[key] = value
                return value
            else:
                print("lvl 1 and 2 cache miss")
                _cache[key] = await f(*args, **kwargs)
                await set_to_dapr(key, _cache[key], ttl)
                return _cache[key]

        return wrapped

    return _cache


@app.get("/get")
@cache(ttl=60)
async def root(key: str):
    return await expensive_function(key)
