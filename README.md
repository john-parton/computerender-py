# Computerender

[![PyPI](https://img.shields.io/pypi/v/computerender.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/computerender.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/computerender)][pypi status]
[![License](https://img.shields.io/pypi/l/computerender)][license]

[![Read the documentation at https://computerender.readthedocs.io/](https://img.shields.io/readthedocs/computerender-py/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/john-parton/computerender-py/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/john-parton/computerender/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/computerender/
[read the docs]: https://computerender-py.readthedocs.io/
[tests]: https://github.com/john-parton/computerender-py/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/john-parton/computerender-py
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- TODO

## Requirements

- TODO

## Installation

You can install _Computerender_ via [pip] from [PyPI]:

```console
$ pip install computerender
```

## Usage

It is recommended to set the `COMPUTERENDER_KEY` environmental variable to your API key.

Otherwise, you can pass it to the `Computerender` class as `api_key`.

Basic usage of asynchronous client.

```python
import asyncio

from computerender import Computerender


async def main():

    async with Computerender() as api:
        data: bytes = api.generate("A cowboy wearing a pink hat", width=512, height=512, guidance=7.5, seed=8675309)
    
    with open("a-cowboy-wearing-a-pink-hat.jpg", "wb") as f:
        f.write(data)


if __name__ == "__main__":
    asyncio.run(main())
```

Sync client is not recommended at this time.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
this python binding for _Computerender_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/john-parton/computerender-py/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/john-parton/computerender-py/blob/main/LICENSE
[contributor guide]: https://github.com/john-parton/computerender-py/blob/main/CONTRIBUTING.md
[command-line reference]: https://computerender-py.readthedocs.io/en/latest/usage.html
