"""Generate the deterministic demo dataset used by scripts/screenshots.py.

Run with: uv run python scripts/generate_mock.py
Writes mock/demo.csv (2,000 orders, 35 columns) covering every dtype dtypeflow
can infer: Boolean, unsigned/signed integers, Float16/32/64, String, Dictionary.
"""

from __future__ import annotations

import csv
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "mock" / "demo.csv"
ROWS = 2_000
SEED = 20240101

COUNTRIES = {
    "CA": ("CAD", 0.05, ("Calgary", "Toronto", "Vancouver", "Montreal")),
    "DE": ("EUR", 0.19, ("Berlin", "Hamburg", "Munich", "Cologne")),
    "FR": ("EUR", 0.20, ("Bordeaux", "Lyon", "Paris", "Marseille")),
    "GB": ("GBP", 0.20, ("Bristol", "London", "Manchester", "Leeds")),
    "JP": ("JPY", 0.10, ("Tokyo", "Osaka", "Kobe", "Nagoya")),
    "US": ("USD", 0.00, ("Austin", "Chicago", "Denver", "Seattle")),
}
WAREHOUSES = {
    "CA": "NYC-02",
    "US": "NYC-02",
    "DE": "BER-01",
    "FR": "PAR-01",
    "GB": "LON-01",
    "JP": "TOK-01",
}
PRODUCTS = {
    "Accessories": ("ACC", ("Backpack", "Cable Organizer", "Mouse Pad", "Tripod")),
    "Electronics": (
        "ELE",
        ("Headphones", "Mechanical Keyboard", "Smart Plug", "Fitness Tracker"),
    ),
    "Fitness": ("FIT", ("Dumbbell Set", "Foam Roller", "Resistance Bands", "Yoga Mat")),
    "Home": ("HOM", ("Coffee Grinder", "Electric Kettle", "Water Bottle", "Desk Lamp")),
    "Office": ("OFF", ("Desk Organizer", "Laptop Stand", "Monitor Arm", "Notebook")),
}
PRICE_RANGE = {
    "Accessories": (5.14, 89.99),
    "Electronics": (29.99, 899.64),
    "Fitness": (9.99, 249.99),
    "Home": (12.49, 199.99),
    "Office": (7.99, 399.99),
}
SALES_CHANNELS = ("marketplace", "mobile_app", "retail_store", "website")
SEGMENTS = ("business", "loyal", "new", "regular")
PAYMENT_METHODS = ("bank_transfer", "card", "paypal", "wallet")
STATUSES = ("cancelled", "delivered", "processing", "returned", "shipped")
STATUS_WEIGHTS = (6, 58, 8, 6, 22)
DISCOUNTS = (0.05, 0.1, 0.15, 0.2, 0.25)
CAMPAIGNS = ("holiday", "newsletter", "referral", "retargeting", "spring_sale")
PROMO_CODES = ("FREESHIP", "SAVE15", "SPRING20", "VIP25", "WELCOME10")
SUPPORT_NOTES = (
    "Address confirmed by support",
    "Customer requested invoice",
    'Customer wrote: "please call first"',
    "Delivery window: 9-12, weekdays",
    "Gift wrap requested",
    "Leave at reception",
    "Reschedule needed",
)
SHIPPING_COSTS = tuple(round(3.5 + 0.32 * step, 2) for step in range(46))
START_DATE = datetime(2024, 1, 1, tzinfo=UTC)


def _postal_code(rng: random.Random, country: str) -> str:
    if country == "GB":
        return (
            f"{rng.choice('BELMSW')}{rng.choice('ABCDEFGHJKLMNPRSTUVWXY')}"
            f"{rng.randint(1, 9)}{rng.choice('ABCDEFGHJKLMNPRSTUVWXY')} "
            f"{rng.randint(1, 9)}{rng.choice('ABDEFGHJLNPQRSTUWXYZ')}"
            f"{rng.choice('ABDEFGHJLNPQRSTUWXYZ')}"
        )
    if country == "CA":
        letters = "ABCEGHJKLMNPRSTVWXYZ"
        return (
            f"{rng.choice('KLMNPRSTVX')}{rng.randint(0, 9)}{rng.choice(letters)}"
            f" {rng.randint(0, 9)}{rng.choice(letters)}{rng.randint(0, 9)}"
        )
    if country == "JP":
        return f"{rng.randint(100, 199)}-{rng.randint(0, 99):04d}"
    return f"{rng.randint(100, 1600):05d}"


def _session_id(rng: random.Random) -> str:
    digits = "".join(rng.choice("0123456789abcdef") for _ in range(32))
    return f"{digits[:8]}-{digits[8:12]}-{digits[12:16]}-{digits[16:20]}-{digits[20:]}"


def _row(rng: random.Random, index: int, order_ids: set[str]) -> dict[str, str]:
    order_date = START_DATE + timedelta(days=rng.randint(0, 899))
    while True:
        order_id = f"ORD-{order_date:%Y%m}-{rng.randint(1, 999_999):06d}"
        if order_id not in order_ids:
            order_ids.add(order_id)
            break

    country = rng.choice(tuple(COUNTRIES))
    currency, tax_rate, cities = COUNTRIES[country]
    category = rng.choice(tuple(PRODUCTS))
    sku_prefix, names = PRODUCTS[category]
    status = rng.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
    shipped = status in {"delivered", "returned", "shipped"}

    quantity = rng.randint(1, 12)
    low, high = PRICE_RANGE[category]
    # Pin the extremes so the profile always shows the full price range.
    unit_price = {0: 5.14, 1: 899.64}.get(index, round(rng.uniform(low, high), 2))
    discount = rng.choice(DISCOUNTS)
    net = quantity * unit_price * (1 - discount)
    tax = round(net * tax_rate, 2)
    shipping = 0.0 if rng.random() < 0.15 else rng.choice(SHIPPING_COSTS)
    total = round(net + tax + shipping, 2)

    shipped_at = (
        order_date
        + timedelta(days=rng.randint(1, 3), hours=rng.randint(0, 23))
        + timedelta(minutes=rng.randint(0, 59))
    )
    warehouse = WAREHOUSES[country]
    if country == "US":
        warehouse = rng.choice(("NYC-02", "AMS-02"))
    tracking = str(rng.randint(1_896_308_983, 999_231_933_169)) if shipped else ""
    return {
        "order_id": order_id,
        "customer_id": f"CUST-{index + 1 if index < 621 else rng.randint(1, 621):05d}",
        "order_date": f"{order_date:%Y-%m-%d}",
        "shipped_at": f"{shipped_at:%Y-%m-%dT%H:%M:00Z}" if shipped else "",
        "country_code": country,
        "city": rng.choice(cities),
        "currency": currency,
        "sales_channel": rng.choice(SALES_CHANNELS),
        "customer_segment": rng.choice(SEGMENTS),
        "product_category": category,
        "product_name": rng.choice(names),
        "sku": f"{sku_prefix}-{rng.randint(1000, 9999)}",
        "quantity": str(quantity),
        "unit_price": f"{unit_price:.2f}",
        "discount_rate": str(discount),
        "tax_amount": f"{tax:.2f}",
        "shipping_cost": f"{shipping:.2f}",
        "order_total": f"{total:.2f}",
        "payment_method": rng.choice(PAYMENT_METHODS),
        "is_paid": "false" if status in {"cancelled", "processing"} else "true",
        "order_status": status,
        "is_gift": "true" if rng.random() < 0.12 else "false",
        "customer_rating": str(rng.randint(1, 5)),
        "delivery_days": str(rng.randint(1, 14)),
        "inventory_change": "0" if status == "cancelled" else str(-quantity),
        "warehouse_stock": str(rng.randint(-2, 31_958)),
        "warehouse_code": warehouse,
        "campaign": rng.choice(CAMPAIGNS) if rng.random() < 0.6 else "",
        "promo_code": rng.choice(PROMO_CODES) if rng.random() < 0.4 else "",
        "tracking_number": tracking,
        "postal_code": _postal_code(rng, country),
        "session_id": _session_id(rng),
        "latitude": f"{rng.uniform(-54.818858, 67.991413):.6f}",
        "longitude": f"{rng.uniform(-124.930150, 144.934858):.6f}",
        "support_note": rng.choice(SUPPORT_NOTES) if rng.random() < 0.1 else "",
    }


def main() -> None:
    rng = random.Random(SEED)
    order_ids: set[str] = set()
    rows = [_row(rng, index, order_ids) for index in range(ROWS)]
    rows[2]["latitude"], rows[3]["latitude"] = "-54.818858", "67.991413"
    rows[2]["longitude"], rows[3]["longitude"] = "-124.930150", "144.934858"
    rows[4]["warehouse_stock"], rows[5]["warehouse_stock"] = "-2", "31958"
    shipped_rows = [row for row in rows if row["tracking_number"]]
    shipped_rows[0]["tracking_number"] = "1896308983"
    shipped_rows[1]["tracking_number"] = "999231933169"

    OUT_PATH.parent.mkdir(exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
