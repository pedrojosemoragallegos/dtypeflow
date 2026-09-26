from __future__ import annotations

from typing import Final, final

from dtypeflow.core.dtype.base import Sizeable
from dtypeflow.core.dtype.primitive.integer.base import Integer


class Signed(Integer, Sizeable): ...


@final
class Int8(Signed):
    SIZE: Final[int] = 1
    LOWER_BOUND: Final[int] = -128
    HIGHER_BOUND: Final[int] = 127


@final
class Int16(Signed):
    SIZE: Final[int] = 2
    LOWER_BOUND: Final[int] = -32768
    HIGHER_BOUND: Final[int] = 32767


@final
class Int32(Signed):
    SIZE: Final[int] = 4
    LOWER_BOUND: Final[int] = -2147483648
    HIGHER_BOUND: Final[int] = 2147483647


@final
class Int64(Signed):
    SIZE: Final[int] = 8
    LOWER_BOUND: Final[int] = -9223372036854775808
    HIGHER_BOUND: Final[int] = 9223372036854775807
