from __future__ import annotations

from typing import final

from typing_extensions import override

from dtypeflow.core.dtype.base import Dtype


@final
class Dictionary(Dtype):
    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
