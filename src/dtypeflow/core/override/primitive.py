from __future__ import annotations

from decimal import Decimal, InvalidOperation

import pyarrow as pa

from .base import Override


class Boolean(Override):
    def __init__(self, column: str, /, *, true_value: str, false_value: str) -> None:
        super().__init__(column)
        if (true_value := true_value.strip().lower()) == (
            false_value := false_value.strip().lower()
        ):
            msg = f"true_value and false_value must differ for column {column!r}: {true_value!r}."
            raise ValueError(msg)
        self._true_value: str = true_value
        self._false_value: str = false_value

    def _coerce(self, value: str | None, /) -> bool | None:
        if value is None or not value.strip():
            return None
        if (value := value.strip().lower()) not in (
            self._true_value,
            self._false_value,
        ):
            msg = f"{value!r} is neither {self._true_value!r} nor {self._false_value!r} for column {self.column!r}."
            raise ValueError(msg)
        return value == self._true_value

    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.bool_())


class Integer(Override):
    def _coerce(self, value: str | None, /) -> int | None:
        if value is None or not value.strip():
            return None
        stripped = value.strip()
        try:
            return int(Decimal(stripped))
        except InvalidOperation:
            msg = f"{stripped!r} is not a valid number for column {self.column!r}."
            raise ValueError(msg) from None


class Int8(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.int8())


class Int16(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.int16())


class Int32(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.int32())


class Int64(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.int64())


class UInt8(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.uint8())


class UInt16(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.uint16())


class UInt32(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.uint32())


class UInt64(Integer):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.uint64())


class Float(Override):
    def _coerce(self, value: str | None, /) -> float | None:
        if value is None or not value.strip():
            return None
        return float(value.strip())


class Float16(Float):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.float16())


class Float32(Float):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.float32())


class Float64(Float):
    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.float64())


class String(Override):
    def _coerce(self, value: str | None, /) -> str | None:
        if value is None or not value.strip():
            return None
        return value.strip()

    def transform(self, *values: str | None) -> pa.Array:
        return pa.array([self._coerce(value) for value in values], type=pa.string())


class Dictionary(String):
    def __init__(self, column: str, /, *categories: str, ordered: bool = False) -> None:
        super().__init__(column)
        if not categories:
            msg = f"categories must be provided for column {column!r}."
            raise ValueError(msg)
        if len(set(categories)) != len(categories):
            msg = f"categories must not contain duplicates for column {column!r}: {categories!r}."
            raise ValueError(msg)
        self._ordered: bool = ordered
        self._categories: tuple[str, ...] = categories

    def _dictionary_index_type(self, num_unique: int, /) -> pa.DataType:
        if num_unique <= 2**8:
            return pa.int8()
        if num_unique <= 2**16:
            return pa.int16()
        if num_unique <= 2**32:
            return pa.int32()
        return pa.int64()

    def transform(self, *values: str | None) -> pa.Array:
        coerced: list[str | None] = [self._coerce(value) for value in values]
        if missing := (
            {value for value in coerced if value is not None} - set(self._categories)
        ):
            msg = f"values {sorted(missing)!r} for column {self.column!r} are not in the provided categories {self._categories!r}."
            raise ValueError(msg)
        rank: dict[str, int] = {
            category: index for (index, category) in enumerate(self._categories)
        }
        return pa.DictionaryArray.from_arrays(
            pa.array(
                [None if value is None else rank[value] for value in coerced],
                type=self._dictionary_index_type(len(self._categories)),
            ),
            pa.array(self._categories, type=pa.string()),
            ordered=self._ordered,
        )
