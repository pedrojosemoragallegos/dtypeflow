from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Dtype(ABC):
    @abstractmethod
    def __repr__(self) -> str: ...


@runtime_checkable
class Sizeable(Protocol):
    SIZE: int
