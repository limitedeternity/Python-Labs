import sys
import math
import itertools
from os import PathLike
from typing import Union


def wc(filename: Union[PathLike, int]) -> (int, int, int):
    with open(filename, "r", encoding="utf-8") as f:
        line_c = word_c = byte_c = 0

        for line in f:
            line_c += 1
            word_c += len(line.split())
            byte_c += len(line)

        return line_c, word_c, byte_c


def fmt(*, width):
    def impl(line_c: int, word_c: int, byte_c: int, file: str) -> str:
        return " ".join(
            itertools.chain(
                (f"{{{var}:{width}d}}" for var in ("line_c", "word_c", "byte_c")),
                ("{file}",),
            )
        ).format(line_c=line_c, word_c=word_c, byte_c=byte_c, file=file)

    return impl


def max_width(*xs: int):
    return max(*map(lambda x: math.floor(math.log10(x)) + 1, xs))


def main():
    files = sys.argv[1:]
    if not files:
        print(fmt(width=7)(*wc(0), ""))
        return

    file_stats = {file: wc(file) for file in files}
    multiple = len(files) > 1

    if multiple:
        file_stats["total"] = tuple(map(sum, zip(*file_stats.values())))

    width = max_width(*itertools.chain(*file_stats.values()))
    for file, stats in file_stats.items():
        print(fmt(width=width)(*stats, file))


if __name__ == "__main__":
    main()
