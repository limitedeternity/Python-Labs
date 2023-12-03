import itertools
from numbers import Number
from os import PathLike
from pathlib import Path
from pprint import pformat as pf

import numpy as np
from numpy.lib.mixins import NDArrayOperatorsMixin


class GetterSetterMixin:
    def __init__(self, value):
        self._value = np.asarray(value)

        if hasattr(self, "__post_init__"):
            self.__post_init__()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = np.asarray(new_value)


class StrMixin:
    def __str__(self):
        return f"{self.__class__.__name__}(\n{pf(self.value.tolist(), indent=4)}\n)"


class FileMixin:
    def write_to_file(self, filename: PathLike) -> None:
        artifacts_dir = Path(__file__).parent / "artifacts" / "02"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        with (artifacts_dir / filename).open(mode="w", encoding="utf-8") as f:
            f.write(str(self))


class ArrayLike(GetterSetterMixin, StrMixin, FileMixin, NDArrayOperatorsMixin):
    _HANDLED_TYPES = ()
    _VALUE_ATTR = "value"

    def __post_init__(self):
        self._HANDLED_TYPES = (np.ndarray, list, Number, ArrayLike)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        out = kwargs.get("out", ())

        for x in itertools.chain(inputs, out):
            if not isinstance(x, self._HANDLED_TYPES):
                return NotImplemented

        inputs = tuple(ArrayLike._unwrap_arraylike(inputs))

        if out:
            kwargs["out"] = tuple(ArrayLike._unwrap_arraylike(out))

        result = getattr(ufunc, method)(*inputs, **kwargs)

        if isinstance(result, tuple):
            return tuple(ArrayLike(x) for x in result)

        if method == "at":
            return None

        return ArrayLike(result)

    @classmethod
    def _unwrap_arraylike(cls, values):
        return (
            getattr(x, cls._VALUE_ATTR) if isinstance(x, ArrayLike) else x
            for x in values
        )


if __name__ == "__main__":
    np.random.seed(0)

    mdata1 = np.random.randint(0, 10, (10, 10))
    mdata2 = np.random.randint(0, 10, (10, 10))
    m1 = ArrayLike(mdata1.tolist())
    m2 = ArrayLike(mdata2.tolist())

    (m1 + m2).write_to_file("matrix_add.txt")
    (m1 * m2).write_to_file("matrix_mul.txt")
    (m1 @ m2).write_to_file("matrix_dot.txt")
