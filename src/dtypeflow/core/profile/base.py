from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from dtypeflow.core.candidate import Candidate
    from dtypeflow.core.dtype import Dtype


class Profile(ABC):
    DTYPE: ClassVar[type[Dtype]]

    def __init__(
        self,
        *values: str | None,
        uniques: tuple[int, ...],
        non_nan: tuple[int, ...],
        nan: tuple[int, ...],
    ) -> None:
        self._values: tuple[str | None, ...] = values
        self._non_nan_indices: tuple[int, ...] = non_nan
        self._nan_indices: tuple[int, ...] = nan
        self._uniques: tuple[int, ...] = uniques
        self._candidates: tuple[Candidate, ...] | None = None

    def uniques(self, *, n: int | None = None) -> tuple[str, ...]:
        if n is None:
            return tuple(self._values[index] for index in self._uniques)
        return tuple(self._values[index] for index in self._uniques[:n])

    @property
    def num_unique(self) -> int:
        return len(self._uniques)

    @property
    def total(self) -> int:
        return len(self._non_nan_indices)

    @property
    def candidates(self) -> tuple[Candidate, ...]:
        if self._candidates is None:
            self._candidates: tuple[Candidate, ...] = self._compute_candidates()
        return self._candidates

    @abstractmethod
    def _compute_candidates(self) -> tuple[Candidate, ...]: ...

    @abstractmethod
    def __repr__(self) -> str: ...
