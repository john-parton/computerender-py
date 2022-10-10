import asyncio
from decimal import Decimal

from .api import Api


# These methods are a repetitive


async def _generate_once(prompt, *args, **kwargs) -> bytes:
    api_key = kwargs.pop("api_key", None)

    async with Api(api_key=api_key) as api:
        return api.generate(prompt, *args, **kwargs)


async def _cost_once(prompt, *args, **kwargs) -> Decimal:
    api_key = kwargs.pop("api_key", None)

    async with Api(api_key=api_key) as api:
        return api.cost(prompt, *args, **kwargs)


# Sync wrappers


def generate_sync(*args, **kwargs) -> bytes:
    return asyncio.run(_generate_once(*args, **kwargs))


def cost_sync(*args, **kwargs) -> Decimal:
    return asyncio.run(_cost_once(*args, **kwargs))
