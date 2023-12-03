from dataclasses import astuple, dataclass
from itertools import groupby
from pprint import pformat as pf
import operator
from pathlib import Path
import numpy as np


def all_equal(iterable) -> bool:
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


@dataclass
class Dimensions:
    rows: int
    cols: int

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class Matrix:
    matrix: [[int]]

    def __post_init__(self):
        self.dims_checked = False

    @property
    def shape(self) -> Dimensions:
        if not self.dims_checked:
            if not all_equal(len(row) for row in self.matrix):
                raise ValueError("Matrix has inconsistent row sizes")

            self.dims_checked = True

        rows = len(self.matrix)
        cols = len(self.matrix[0])
        return Dimensions(rows, cols)

    def __getitem__(self, i: int) -> [int]:
        return self.matrix[i]

    def __str__(self) -> str:
        return pf(self.matrix)

    @classmethod
    def map(cls, func, *matrices):
        if not all_equal(m.shape for m in matrices):
            raise ValueError("Matrices must have the same dimensions")

        if not matrices:
            raise RuntimeError("What did you expect?")

        rows, cols = matrices[0].shape
        new = Matrix([[0 for c in range(cols)] for r in range(rows)])

        for r in range(rows):
            for c in range(cols):
                new[r][c] = func(*(m[r][c] for m in matrices))

        return new

    def __add__(self, other):
        return Matrix.map(operator.add, self, other)

    def __sub__(self, other):
        return Matrix.map(operator.sub, self, other)

    def __mul__(self, other):
        return Matrix.map(operator.mul, self, other)

    def __matmul__(self, other):
        self_row, self_col = self.shape
        other_row, other_col = other.shape

        if self_col != other_row:
            raise ValueError("Incompatible matrix dimensions for multiplication")

        new = Matrix([[0 for c in range(other_col)] for r in range(self_row)])

        for i in range(self_row):
            for j in range(self_col):
                for k in range(other_col):
                    new[i][k] += self[i][j] * other[j][k]

        return new


if __name__ == "__main__":
    np.random.seed(0)

    mdata1 = np.random.randint(0, 10, (10, 10))
    mdata2 = np.random.randint(0, 10, (10, 10))
    m1 = Matrix(mdata1.tolist())
    m2 = Matrix(mdata2.tolist())

    artifacts_dir = Path(__file__).parent / "artifacts" / "01"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    with (artifacts_dir / "matrix_add.txt").open(mode="w", encoding="utf-8") as f:
        m_add = m1 + m2
        numpy_add = (mdata1 + mdata2).tolist()

        add_eq = m_add == Matrix(numpy_add)
        assert add_eq

        f.write(f"Custom:\n{m_add}")
        f.write("\n")
        f.write(f"NumPy:\n{pf(numpy_add)}")
        f.write("\n")
        f.write(f"Equal: {add_eq}")

    with (artifacts_dir / "matrix_mul.txt").open(mode="w", encoding="utf-8") as f:
        m_mul = m1 * m2
        numpy_mul = (mdata1 * mdata2).tolist()

        mul_eq = m_mul == Matrix(numpy_mul)
        assert mul_eq

        f.write(f"Custom:\n{m_mul}")
        f.write("\n")
        f.write(f"NumPy:\n{pf(numpy_mul)}")
        f.write("\n")
        f.write(f"Equal: {mul_eq}")

    with (artifacts_dir / "matrix_dot.txt").open(mode="w", encoding="utf-8") as f:
        m_matmul = m1 @ m2
        numpy_matmul = (mdata1 @ mdata2).tolist()

        matmul_eq = m_matmul == Matrix(numpy_matmul)
        assert matmul_eq

        f.write(f"Custom:\n{m_matmul}")
        f.write("\n")
        f.write(f"NumPy:\n{pf(numpy_matmul)}")
        f.write("\n")
        f.write(f"Equal: {matmul_eq}")
