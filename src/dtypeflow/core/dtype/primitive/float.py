from __future__ import annotations

from decimal import Decimal
from typing import ClassVar, Final, final

from typing_extensions import override

from dtypeflow.core.dtype.base import Sizeable

from .base import Primitive


class Float(Primitive, Sizeable):
    MAX_ABSOLUTE_VALUE: ClassVar[Decimal]
    MAX_SIGNIFICANT_DIGITS: ClassVar[int]

    @override
    def __repr__(self) -> str:
        return f"Float(±{self.MAX_ABSOLUTE_VALUE} (≈ {self.MAX_SIGNIFICANT_DIGITS} significant digits))"


@final
class Float16(Float):
    SIZE: Final[int] = 2
    MAX_ABSOLUTE_VALUE: Final[Decimal] = Decimal(65504)
    MAX_SIGNIFICANT_DIGITS: Final[int] = 4


@final
class Float32(Float):
    SIZE: Final[int] = 4
    MAX_ABSOLUTE_VALUE: Final[Decimal] = Decimal("3.4028235e38")
    MAX_SIGNIFICANT_DIGITS: Final[int] = 7


@final
class Float64(Float):
    SIZE: Final[int] = 8
    MAX_ABSOLUTE_VALUE: Final[Decimal] = Decimal("1.7976931348623157e308")
    MAX_SIGNIFICANT_DIGITS: Final[int] = 15
