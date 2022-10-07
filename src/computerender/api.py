import asyncio

import io
from decimal import Decimal as D
import os
import typing 
from urllib.parse import quote_plus

# from typing import TypedDict

import aiohttp 
from PIL import Image



class SafetyError(ValueError):
    pass


class TermError(SafetyError):
    pass


class ContentError(SafetyError):
    pass

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

    # Check if the image is completely black
    def _check_nsfw(self, data: bytes) -> bool:
        im = Image.open(io.BytesIO(data))

        # https://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
        return not im.getbbox()

    def _format_url(self, prefix: str, prompt: str) -> str:
        return f"{self.BASE_URL}{prefix}/{quote_plus(prompt)}"

    async def generate(self, prompt: str, **kwargs) -> bytes:
        request_url: str = self._format_url("generate", prompt)

        async with self.session.get(request_url, params=kwargs) as response:
            if response.status == 400:
                raise TermError(f"{prompt!r} triggered computerender keyword check")

            elif response.staus != 200:
                raise ValueError("Got non-200 status code")

            # TODO Handle other status codes

            # TODO Handle out of credits, wrong API key, etc.

            body = await response.read()

            if self._check_nsfw(body):
                raise ContentError(f"{prompt!r} triggered computerender post-generation check")

            return body
    
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

    # Allows using the API as a context manager
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args, **kwargs):
        await self.close()



# Not really tested at the moment
class SyncApi(Api):
    def generate(self, *args, **kwargs):
        return asyncio.run(super().generate(*args, **kwargs))

    def cost(self, *args, **kwargs):
        return asyncio.run(super().cost(*args, **kwargs))

    def close(self):
        asyncio.run(self.session.close())
