from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyarrow as pa


class Override(ABC):
    def __init__(self, column: str, /) -> None:
        self._column: str = column

    @property
    def column(self) -> str:
        return self._column

    @abstractmethod
    def transform(self, *values: str | None) -> pa.Array: ...

    def __repr__(self) -> str:
        return f"{type(self).__name__}(column={self._column!r})"
