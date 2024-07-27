__all__ = "sleep"

import asyncio


async def sleep():
    await asyncio.sleep(0.5)
