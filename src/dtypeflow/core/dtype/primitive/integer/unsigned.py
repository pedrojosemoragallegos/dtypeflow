from __future__ import annotations

from typing import Final, final

from dtypeflow.core.dtype.base import Sizeable
from dtypeflow.core.dtype.primitive.integer.base import Integer


class Unsigned(Integer, Sizeable): ...


@final
class UInt8(Unsigned):
    SIZE: Final[int] = 1
    LOWER_BOUND: Final[int] = 0
    HIGHER_BOUND: Final[int] = 255


@final
class UInt16(Unsigned):
    SIZE: Final[int] = 2
    LOWER_BOUND: Final[int] = 0
    HIGHER_BOUND: Final[int] = 65535


@final
class UInt32(Unsigned):
    SIZE: Final[int] = 4
    LOWER_BOUND: Final[int] = 0
    HIGHER_BOUND: Final[int] = 4294967295


@final
class UInt64(Unsigned):
    SIZE: Final[int] = 8
    LOWER_BOUND: Final[int] = 0
    HIGHER_BOUND: Final[int] = 18446744073709551615
