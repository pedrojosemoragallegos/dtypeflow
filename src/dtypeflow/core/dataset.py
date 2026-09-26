from __future__ import annotations

from collections.abc import Iterator, Mapping
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtypeflow.core.dtype import Dtype
    from dtypeflow.core.profile import Profile


class Dataset(Mapping[str, "Profile"]):
    def __init__(self, source: str | Path, /, **profiles: Profile) -> None:
        if isinstance(source, str):
            source: Path = Path(source)
        self._source: Path = source
        self._profiles: MappingProxyType[str, Profile] = MappingProxyType(profiles)

    @property
    def source(self) -> Path:
        return self._source

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(self._profiles.keys())

    @property
    def dtypes(self) -> MappingProxyType[str, type[Dtype]]:
        return MappingProxyType(
            {column: profile.DTYPE for (column, profile) in self._profiles.items()},
        )

    def __getitem__(self, column: str) -> Profile:
        return self._profiles[column]

    def __iter__(self) -> Iterator[str]:
        return iter(self._profiles)

    def __len__(self) -> int:
        return len(self._profiles)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(source={self._source!r}, columns={self.columns!r})"
        )
