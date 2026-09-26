# Hierachie

```markdown
DataType
│
├── Primitive
│   ├── Boolean                  → 1 bit (stored bitmap; ≈ 0.125 bytes/value)
│   │
│   ├── Integer
│   │   ├── Signed
│   │   │   ├── Int8             → 1 byte
│   │   │   ├── Int16            → 2 bytes
│   │   │   ├── Int32            → 4 bytes
│   │   │   └── Int64            → 8 bytes
│   │   │
│   │   └── Unsigned
│   │       ├── UInt8            → 1 byte
│   │       ├── UInt16           → 2 bytes
│   │       ├── UInt32           → 4 bytes
│   │       └── UInt64           → 8 bytes
│   │
│   ├── Float
│   │   ├── Float16             → 2 bytes
│   │   ├── Float32             → 4 bytes
│   │   └── Float64             → 8 bytes
│   │
│   └── Decimal                  → 16 bytes (Decimal128) 32 bytes (Decimal256)
│
├── Temporal
│   ├── Date32                   → 4 bytes
│   ├── Date64                   → 8 bytes
│   ├── Time32                   → 4 bytes
│   ├── Time64                   → 8 bytes
│   ├── Timestamp                → 8 bytes
│   └── Duration                 → 8 bytes
│
├── Binary
│   ├── Binary                   → variable-length
│   ├── LargeBinary              → variable-length
│   ├── String                   → variable-length (UTF-8)
│   └── LargeString              → variable-length (UTF-8)
│
├── Nested
│   ├── List                     → variable-length
│   ├── LargeList                → variable-length
│   ├── Struct                   → sum of cHIGHER_BOUNDld field SIZEs
│   ├── Map                      → variable-length
│   └── Dictionary               → index SIZE (1, 2, 4, or 8 bytes)
│
└── Null                         → 0 bytes
```
