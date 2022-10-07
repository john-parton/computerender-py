import asyncio
import io
import os
import typing
from decimal import Decimal
from urllib.parse import quote_plus

import aiohttp
from PIL import Image


# from typing import TypedDict


class ApiError(ValueError):
    pass


class SafetyError(ApiError):
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
    """Wrapper around computerender HTTP API
    
    Generate images using Stable Diffusion"""

    BASE_URL = f"https://api.computerender.com/"

    KWARG_ALIASES = [
        ("w", "width"),
        ("h", "height"),
        ("guidance", "cfg_scale"),
    ]

    def __init__(self, api_key: typing.Optional[str] = None):
        """Constructor method
        """
        self.api_key = api_key or os.environ["COMPUTERENDER_KEY"]
        self.headers = {"Authorization": f"X-API-Key {self.api_key}"}
        # I think there's a way to get running event loop here and pass it in optionally
        # or maybe even lazily
        # One of my other libs does something similar
        self.session = aiohttp.ClientSession(headers=self.headers)

    def _parse_currency(self, value: str) -> Decimal:
        currency_type, amount = value[0], value[1:]

        if currency_type != "$":
            raise ValueError(f"Expected US dollars, got {value!r}")

        return Decimal(amount)

    # Check if the image is completely black
    def _check_nsfw(self, data: bytes) -> bool:
        im = Image.open(io.BytesIO(data))

        # https://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
        return not im.getbbox()

    def _format_url(self, prefix: str, prompt: str) -> str:
        return f"{self.BASE_URL}{prefix}/{quote_plus(prompt)}"

    # This would probably be easier with pydantic or attrs, but I don't want
    # to add a dep just for this
    def _clean_kwargs(self, kwargs: typing.Mapping[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        for key, alias in self.KWARG_ALIASES:
            if key in kwargs and alias in kwargs:
                raise ValueError(
                    f"Do not pass both {key!r} and {alias!r} as keyword arguments"
                )

            if alias in kwargs:
                kwargs[key] = kwargs.pop(alias)

        extra_keys = kwargs.keys() - {"w", "h", "seed", "guidance", "iterations"}

        if extra_keys:
            raise ValueError(
                f"Invalid keys passed to Computerender api: {', '.join(map(repr, extra_keys))}"
            )

        return kwargs

    async def generate(self, prompt: str, **kwargs) -> bytes:
        """Returns byte string of generated image. Byte string is JPEG formatted image.
        
        Raises an exception if image could not be generated."""
        kwargs = self._clean_kwargs(kwargs)

        request_url: str = self._format_url("generate", prompt)

        async with self.session.get(request_url, params=kwargs) as response:
            if response.status == 400:

                data = await response.json()

                if data.get("status", "") == "error":
                    error_message = data.get("message", "")

                    if error_message == "potentially unsafe words in prompt":
                        raise TermError(f"{prompt!r} triggered computerender keyword check")
                    else:
                        raise ApiError(f"API Error: {error_message!r}")

                else:
                    raise ValueError(f"Computerender HTTP400: {data}")

            elif response.status != 200:
                raise ValueError("Got non-200 status code")

            else:

                # TODO Handle other status codes

                # TODO Handle out of credits, wrong API key, etc.

                body = await response.read()

                if self._check_nsfw(body):
                    raise ContentError(
                        f"{prompt!r} triggered computerender post-generation check"
                    )

                return body

    # TODO improve the annotation here
    async def cost(self, prompt: str, **kwargs) -> Decimal:
        """Returns cost to generate image."""
        kwargs = self._clean_kwargs(kwargs)

        request_url: str = self._format_url("cost", prompt)

        async with self.session.get(request_url, params=kwargs) as response:
            data: dict = await response.json()

            return self._parse_currency(data["cost"])

    # Close the API
    # Should be called if the API is no longer being used
    async def close(self) -> None:
        await self.session.close()

    # Allows using the API as a context manager
    async def __aenter__(self):
        return self

    # TODO Fix parameters
    async def __aexit__(self, *args, **kwargs) -> None:
        await self.close()


# Not really tested at the moment
# Causes mypy type errors due to type mismatch of methods
class SyncApi(Api):
    def generate(self, *args, **kwargs) -> bytes:
        return asyncio.run(super().generate(*args, **kwargs))

    def cost(self, *args, **kwargs) -> Decimal:
        return asyncio.run(super().cost(*args, **kwargs))

    def close(self) -> None:
        asyncio.run(self.session.close())
