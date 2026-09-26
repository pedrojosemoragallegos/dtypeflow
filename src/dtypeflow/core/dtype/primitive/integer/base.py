from __future__ import annotations

from typing import ClassVar

from typing_extensions import override

from dtypeflow.core.dtype.base import Sizeable
from dtypeflow.core.dtype.primitive.base import Primitive


class Integer(Primitive, Sizeable):
    LOWER_BOUND: ClassVar[int]
    HIGHER_BOUND: ClassVar[int]

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.LOWER_BOUND} – {self.HIGHER_BOUND})"
