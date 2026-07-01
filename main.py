import tomllib
import uvicorn
import asyncio
from uuid import uuid4
from fastapi import FastAPI

from src.ai_agents.voice_text_flows import local_voice_call

with open("pyproject.toml", "rb") as _f:
    _version = tomllib.load(_f)["project"]["version"]

app = FastAPI(title="Simple Voice Agent", version=_version)

@app.post("/api/calling_assistant")
async def calling_assistant(call_id: str = str(uuid4())):
    await local_voice_call(
        call_id=call_id
    )

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level='info')
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())