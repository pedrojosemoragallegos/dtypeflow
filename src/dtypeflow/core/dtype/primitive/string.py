from __future__ import annotations

from typing import final

from typing_extensions import override

from .base import Primitive


@final
class String(Primitive):
    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
