__all__ = ["sleep"]

import asyncio


async def sleep() -> None:
    """Sleep for a bit of time."""
    await asyncio.sleep(0.5)
