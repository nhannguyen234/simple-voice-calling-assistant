import asyncio
from uuid import uuid4

from src.ai_agents.voice_text_flows import local_voice_call

async def main(call_id=str(uuid4())):
    await local_voice_call(call_id=call_id)

if __name__ == "__main__":
    asyncio.run(main())