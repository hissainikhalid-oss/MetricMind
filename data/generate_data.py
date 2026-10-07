import numpy as np
import pandas as pd
from pathlib import Path

# Reproducible dataset
rng = np.random.default_rng(42)

N_ROWS = 6000

START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2026-09-30")

regions = {
    "Europe": ["Germany", "France", "United Kingdom", "Italy", "Spain"],
    "North America": ["USA", "Canada", "Mexico"],
    "Asia Pacific": ["India", "Japan", "Australia", "Singapore"],
    "Middle East": ["UAE", "Saudi Arabia", "Qatar"],
}

products = [
    ("Laptop Pro", "Technology", 1200),
    ("Business Laptop", "Technology", 900),
    ("Smartphone X", "Technology", 750),
    ("Tablet Air", "Technology", 600),

    ("Office Chair", "Furniture", 320),
    ("Executive Desk", "Furniture", 650),
    ("Bookshelf", "Furniture", 220),
    ("Conference Table", "Furniture", 900),

    ("Printer Paper", "Office Supplies", 30),
    ("Ink Cartridge", "Office Supplies", 80),
    ("Notebook Pack", "Office Supplies", 20),
    ("Desk Organizer", "Office Supplies", 45),
]

# ----------------------------
# Generate transaction dates
# ----------------------------

date_range_days = (END_DATE - START_DATE).days + 1

dates = START_DATE + pd.to_timedelta(
    rng.integers(0, date_range_days, size=N_ROWS),
    unit="D"
)

# ----------------------------
# Generate regions / countries
# ----------------------------

region_names = list(regions.keys())

region_values = rng.choice(
    region_names,
    size=N_ROWS,
    p=[0.30, 0.30, 0.28, 0.12]
)

country_values = [
    rng.choice(regions[region])
    for region in region_values
]

# ----------------------------
# Generate products
# ----------------------------

product_indices = rng.integers(0, len(products), size=N_ROWS)

product_names = []
categories = []
base_prices = []

for index in product_indices:
    product, category, price = products[index]

    product_names.append(product)
    categories.append(category)
    base_prices.append(price)

base_prices = np.array(base_prices, dtype=float)

# ----------------------------
# Units and selling price
# ----------------------------

units_sold = rng.integers(1, 20, size=N_ROWS)

price_noise = rng.normal(
    loc=1.0,
    scale=0.05,
    size=N_ROWS
)

unit_price = base_prices * price_noise

revenue = units_sold * unit_price

# ----------------------------
# Cost generation
# ----------------------------

category_cost_ratio = {
    "Technology": 0.58,
    "Furniture": 0.50,
    "Office Supplies": 0.42,
}

material_cost = np.array([
    revenue[i] * category_cost_ratio[categories[i]]
    for i in range(N_ROWS)
])

# Small random cost variation
material_cost *= rng.normal(
    1.0,
    0.04,
    size=N_ROWS
)

shipping_ratio = {
    "Europe": 0.055,
    "North America": 0.050,
    "Asia Pacific": 0.065,
    "Middle East": 0.070,
}

shipping_cost = np.array([
    revenue[i] * shipping_ratio[region_values[i]]
    for i in range(N_ROWS)
])

shipping_cost *= rng.normal(
    1.0,
    0.08,
    size=N_ROWS
)

operating_cost = revenue * rng.uniform(
    0.08,
    0.14,
    size=N_ROWS
)

# --------------------------------------------------
# Intentional business event:
# Europe suffers cost pressure during Q3 2026.
#
# This gives MetricMind a genuine explanation for:
# "Why did European margins drop in Q3?"
# --------------------------------------------------

years = pd.DatetimeIndex(dates).year
quarters = pd.DatetimeIndex(dates).quarter

europe_q3_2026 = (
    (region_values == "Europe")
    & (years == 2026)
    & (quarters == 3)
)

# Supply / raw-material pressure
material_cost[europe_q3_2026] *= 1.18

# Logistics disruption
shipping_cost[europe_q3_2026] *= 1.45

# ----------------------------
# Final calculated values
# ----------------------------

total_cost = (
    material_cost
    + shipping_cost
    + operating_cost
)

profit = revenue - total_cost

margin = np.where(
    revenue > 0,
    profit / revenue,
    0
)

# ----------------------------
# Build DataFrame
# ----------------------------

df = pd.DataFrame({
    "order_id": [
        f"ORD-{i:06d}"
        for i in range(1, N_ROWS + 1)
    ],

    "date": dates,

    "region": region_values,

    "country": country_values,

    "category": categories,

    "product": product_names,

    "units_sold": units_sold,

    "unit_price": np.round(unit_price, 2),

    "revenue": np.round(revenue, 2),

    "material_cost": np.round(material_cost, 2),

    "shipping_cost": np.round(shipping_cost, 2),

    "operating_cost": np.round(operating_cost, 2),

    "total_cost": np.round(total_cost, 2),

    "profit": np.round(profit, 2),

    "margin": np.round(margin, 4),
})

# Helpful semantic dimensions
df["year"] = pd.to_datetime(df["date"]).dt.year

df["quarter"] = (
    "Q"
    + pd.to_datetime(df["date"])
        .dt.quarter
        .astype(str)
)

df["month"] = (
    pd.to_datetime(df["date"])
    .dt.strftime("%Y-%m")
)

# Sort transactions chronologically
df = df.sort_values("date").reset_index(drop=True)

# ----------------------------
# Save CSV
# ----------------------------

output_path = Path(__file__).parent / "corporate_sales.csv"

df.to_csv(
    output_path,
    index=False
)

print("=" * 60)
print("MetricMind Corporate Dataset Generated")
print("=" * 60)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")

print("\nRegions:")
print(df["region"].value_counts())

print("\nDataset saved to:")
print(output_path)

print("\nSample:")
print(df.head())