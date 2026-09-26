from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from types import MappingProxyType

from typing_extensions import override


class Table(Mapping[str, tuple[str, ...]]):
    def __init__(self, **columns: Iterable[str]) -> None:
        self._values: MappingProxyType[str, tuple[str, ...]] = MappingProxyType(
            {name: tuple(column_values) for (name, column_values) in columns.items()},
        )

    @override
    def __getitem__(self, name: str) -> tuple[str, ...]:
        return self._values[name]

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    @override
    def __len__(self) -> int:
        return len(self._values)

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}({dict(self._values)!r})"
