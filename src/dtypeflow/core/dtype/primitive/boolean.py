from __future__ import annotations

from typing import Final, final

from typing_extensions import override

from dtypeflow.core.dtype.base import Sizeable

from .base import Primitive


@final
class Boolean(Primitive, Sizeable):
    SIZE: Final[int] = 1
    TRUE: Final[bool] = True
    FALSE: Final[bool] = False

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.TRUE}, {self.FALSE})"
