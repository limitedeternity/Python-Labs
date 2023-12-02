from collections import deque
import sys
from os import PathLike
from typing import Union


def tail(filename: Union[PathLike, int], lines: int) -> None:
    with open(filename, "r", encoding="utf-8") as f:
        lines = deque(f, maxlen=lines)

        for line in lines:
            print(line, end="")


def lookahead(iterable):
    it = iter(iterable)
    last = next(it)

    for val in it:
        yield last, True
        last = val

    yield last, False


def main():
    files = sys.argv[1:]

    if not files:
        tail(0, 17)
        return

    multiple = len(files) > 1

    for file, has_more in lookahead(files):
        if multiple:
            print(f"==> {file} <==")

        tail(file, 10)

        if multiple and has_more:
            print("\n", end="")


if __name__ == "__main__":
    main()
