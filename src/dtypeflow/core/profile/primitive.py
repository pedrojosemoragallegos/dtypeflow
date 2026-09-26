from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, Final, cast

from dtypeflow.core.candidate import candidate_factory
from dtypeflow.core.dtype import (
    BooleanDtype,
    Dtype,
    Float16Dtype,
    Float32Dtype,
    Float64Dtype,
    FloatDtype,
    Int8Dtype,
    Int16Dtype,
    Int32Dtype,
    Int64Dtype,
    IntegerDtype,
    StringDtype,
    UInt8Dtype,
    UInt16Dtype,
    UInt32Dtype,
    UInt64Dtype,
)

from .base import Profile

if TYPE_CHECKING:
    from dtypeflow.core.candidate import Candidate


class Boolean(Profile):
    DTYPE: Final[type[Dtype]] = BooleanDtype

    def _compute_candidates(self) -> tuple[Candidate, ...]:
        return candidate_factory(
            self.DTYPE, num_unique=self.num_unique, total=self.total,
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(num_unique={self.num_unique})"


class Integer(Profile):
    DTYPE: ClassVar[type[Dtype]] = IntegerDtype

    @property
    def min(self) -> int:
        return min(int(value) for value in self.uniques())

    @property
    def max(self) -> int:
        return max(int(value) for value in self.uniques())

    def _compute_candidates(self) -> tuple[Candidate, ...]:
        return candidate_factory(
            self.DTYPE,
            num_unique=self.num_unique,
            total=self.total,
            min_value=self.min,
            max_value=self.max,
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(min={self.min}, max={self.max}, num_unique={self.num_unique})"


class UInt8(Integer):
    DTYPE: Final[type[Dtype]] = UInt8Dtype


class UInt16(Integer):
    DTYPE: Final[type[Dtype]] = UInt16Dtype


class UInt32(Integer):
    DTYPE: Final[type[Dtype]] = UInt32Dtype


class UInt64(Integer):
    DTYPE: Final[type[Dtype]] = UInt64Dtype


class Int8(Integer):
    DTYPE: Final[type[Dtype]] = Int8Dtype


class Int16(Integer):
    DTYPE: Final[type[Dtype]] = Int16Dtype


class Int32(Integer):
    DTYPE: Final[type[Dtype]] = Int32Dtype


class Int64(Integer):
    DTYPE: Final[type[Dtype]] = Int64Dtype


class Float(Profile):
    DTYPE: ClassVar[type[Dtype]] = FloatDtype

    @property
    def min(self) -> Decimal:
        return min(Decimal(value) for value in self.uniques())

    @property
    def max(self) -> Decimal:
        return max(Decimal(value) for value in self.uniques())

    @property
    def precision(self) -> int:
        return max(len(Decimal(value).as_tuple().digits) for value in self.uniques())

    @property
    def scale(self) -> int:
        exponents: list[int] = [
            cast("int", Decimal(value).as_tuple().exponent) for value in self.uniques()
        ]
        return max([0, *(-exponent for exponent in exponents)])

    def _compute_candidates(self) -> tuple[Candidate, ...]:
        return candidate_factory(
            self.DTYPE,
            num_unique=self.num_unique,
            total=self.total,
            min_value=self.min,
            max_value=self.max,
            precision=self.precision,
            scale=self.scale,
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(min={self.min}, max={self.max}, precision={self.precision}, scale={self.scale}, num_unique={self.num_unique})"


class Float16(Float):
    DTYPE: Final[type[Dtype]] = Float16Dtype


class Float32(Float):
    DTYPE: Final[type[Dtype]] = Float32Dtype


class Float64(Float):
    DTYPE: Final[type[Dtype]] = Float64Dtype


class String(Profile):
    DTYPE: Final[type[Dtype]] = StringDtype

    @property
    def min_length(self) -> int:
        return min(len(value) for value in self.uniques())

    @property
    def max_length(self) -> int:
        return max(len(value) for value in self.uniques())

    def _compute_candidates(self) -> tuple[Candidate, ...]:
        return candidate_factory(
            self.DTYPE, num_unique=self.num_unique, total=self.total,
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(min_length={self.min_length}, max_length={self.max_length}, num_unique={self.num_unique})"
