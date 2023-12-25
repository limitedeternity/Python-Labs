import argparse
import asyncio
from functools import partial, wraps
import hashlib
from pathlib import Path
import platform
from typing import Tuple

import aiohttp
import aiofiles


def static_vars(**kwargs):
    def decorate(func):
        for k, v in kwargs.items():
            setattr(func, k, v)

        return func

    return decorate


def aiofy(*, executor=None):
    def decorate(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            loop = asyncio.get_running_loop()
            func_binder = partial(func, *args, **kwargs)

            return await loop.run_in_executor(executor, func_binder)

        return wrapper

    return decorate


def to_async_hasher(hasher):
    return type(
        "AsyncHasher",
        (),
        {
            "__module__": __name__,
            "update": aiofy()(hasher.update),
            "digest": aiofy()(hasher.digest),
            "hexdigest": aiofy()(hasher.hexdigest),
        },
    )


async def file_digest(file_path: Path) -> Tuple[Path, str]:
    hasher = to_async_hasher(hashlib.sha256())

    async with aiofiles.open(file_path, mode="rb") as f:
        while chunk := await f.read(1024):
            await hasher.update(chunk)

    return (file_path, await hasher.hexdigest())


@static_vars(hashes=set())
def unique_hash(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while True:
            file_path, file_hash = await file_digest(await func(*args, **kwargs))

            if file_hash in unique_hash.hashes:
                print(f"Rejected: {file_path.name} ({file_hash})")
                await asyncio.sleep(1)

                continue

            unique_hash.hashes.add(file_hash)
            print(f"Passed: {file_path.name} ({file_hash})")

            return file_path

    return wrapper


async def download_file(url: str, file_path: Path) -> Path:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async with aiofiles.open(file_path, mode="wb") as f:
                while chunk := await response.content.read(1024):
                    await f.write(chunk)

    return file_path


async def fetch_persons(n: int, dest: Path) -> Tuple[Path, ...]:
    tasks = [None] * n
    dest.mkdir(parents=True, exist_ok=True)

    for i in range(n):
        tasks[i] = asyncio.create_task(
            unique_hash(download_file)(
                "https://thispersondoesnotexist.com/",
                dest / f"person_{i + 1}.jpeg",
            )
        )

    return await asyncio.gather(*tasks)


def nat_type(x, /) -> int:
    x = int(x)

    if x < 1:
        raise argparse.ArgumentTypeError("Natural number is expected")

    return x


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=nat_type, help="number of persons to download")
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path(__file__).parent / "artifacts" / "01",
        help="destination directory",
    )

    argv = parser.parse_args()

    for path in asyncio.run(fetch_persons(argv.n, argv.dest)):
        print(f"Downloaded: {path.resolve()}")
