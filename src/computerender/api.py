import asyncio

from decimal import Decimal as D
import os
import typing 
from urllib.parse import quote_plus

# from typing import TypedDict

import aiohttp 


# By default all keys are required :/
# class Parameters(TypedDict):
#     seed: int
#     w: int
#     h: int
#     guidance: float
#     iterations: int


class Api:

    BASE_URL = f"https://api.computerender.com/"

    def __init__(self, api_key: typing.Optional[str] = None):
        self.api_key = api_key or os.environ["COMPUTERENDER_KEY"]
        self.headers = {
            "Authorization": f"X-API-Key {self.api_key}"
        }
        self.session = aiohttp.ClientSession(headers=self.headers)

    def _parse_currency(self, value: str) -> D:
        currency_type, amount = value[0], value[1:]

        if currency_type != "$":
            raise ValueError(f"Expected US dollars, got {value}")

        return D(amount)

    def _format_url(self, prefix: str, prompt: str) -> str:
        return f"{self.BASE_URL}{prefix}/{quote_plus(prompt)}"

    async def generate(self, prompt: str, **kwargs) -> bytes:
        request_url: str = self._format_url("generate", prompt)

        async with self.session.get(request_url, params=kwargs) as response:
            return await response.read()
    
    # TODO improve the annotation here
    async def cost(self, prompt: str, **kwargs) -> D:
        request_url: str = self._format_url("cost", prompt)

        async with self.session.get(request_url, params=kwargs) as response:
            data: dict = await response.json()

            return self._parse_currency(data["cost"])

    # Close the API
    # Should be called if the API is no longer being used
    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args, **kwargs):
        await self.close()



class SyncApi(Api):
    def generate(self, *args, **kwargs):
        return asyncio.run(super().generate(*args, **kwargs))

    def cost(self, *args, **kwargs):
        return asyncio.run(super().cost(*args, **kwargs))

    def close(self):
        asyncio.run(self.session.close())
