from __future__ import annotations

from typing import Final

from dtypeflow.core.candidate import Compatibility

GROUP_SAFE: Final[str] = "Safe"
GROUP_TOO_SMALL: Final[str] = "Too small"
GROUP_DISCOURAGED: Final[str] = "Discouraged"
GROUP_INCOMPATIBLE: Final[str] = "Incompatible"
GROUP_ORDER: Final[tuple[str, ...]] = (
    GROUP_SAFE,
    GROUP_TOO_SMALL,
    GROUP_DISCOURAGED,
    GROUP_INCOMPATIBLE,
)
_GROUP_BY_COMPATIBILITY: Final[dict[Compatibility, str]] = {
    Compatibility.FULL_RANGE_FIT: GROUP_SAFE,
    Compatibility.VALUES_PRESERVED: GROUP_SAFE,
    Compatibility.OBSERVED_ONLY_FIT: GROUP_SAFE,
    Compatibility.BOOLEAN_MAPPING: GROUP_SAFE,
    Compatibility.DICTIONARY_ENCODING: GROUP_SAFE,
    Compatibility.RANGE_NO_FIT: GROUP_TOO_SMALL,
    Compatibility.UNEVALUATED_NO_FIT: GROUP_TOO_SMALL,
    Compatibility.PRECISION_REDUCTION: GROUP_DISCOURAGED,
    Compatibility.DECIMAL_TRUNCATION: GROUP_DISCOURAGED,
    Compatibility.DICTIONARY_INEFFICIENT: GROUP_DISCOURAGED,
    Compatibility.VALUES_NO_FIT: GROUP_INCOMPATIBLE,
    Compatibility.NOT_NUMERIC: GROUP_INCOMPATIBLE,
}


def group_of(compatibility: Compatibility, /) -> str:
    return _GROUP_BY_COMPATIBILITY[compatibility]


def is_selectable(compatibility: Compatibility, /) -> bool:
    return group_of(compatibility) != GROUP_INCOMPATIBLE
