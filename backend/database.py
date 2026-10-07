from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "corporate_sales.csv"

DB_PATH = BASE_DIR / "metricmind.db"

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


# ---------------------------------------------------------
# Database engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    future=True
)


def get_engine():
    return engine


# ---------------------------------------------------------
# Load dataset into SQLite
# ---------------------------------------------------------

def load_sales_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    print("=" * 60)
    print("MetricMind Analytics Warehouse")
    print("=" * 60)

    print("\nLoading dataset...")

    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["date"]
    )

    print(f"Rows loaded from CSV: {len(df):,}")

    # Write dataset to database
    df.to_sql(
        "sales",
        con=engine,
        if_exists="replace",
        index=False
    )

    # Create useful indexes
    with engine.begin() as connection:

        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_sales_date
                ON sales(date)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_sales_region
                ON sales(region)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_sales_category
                ON sales(category)
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS
                idx_sales_quarter
                ON sales(year, quarter)
                """
            )
        )

    print("\nDatabase created successfully.")
    print(f"Database: {DB_PATH}")
    print("Table: sales")


# ---------------------------------------------------------
# Verification
# ---------------------------------------------------------

def verify_database():

    with engine.connect() as connection:

        total_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM sales
                """
            )
        ).scalar()

        total_revenue = connection.execute(
            text(
                """
                SELECT SUM(revenue)
                FROM sales
                """
            )
        ).scalar()

        total_profit = connection.execute(
            text(
                """
                SELECT SUM(profit)
                FROM sales
                """
            )
        ).scalar()

        print("\n" + "=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)

        print(
            f"Records in database: {total_rows:,}"
        )

        print(
            f"Total Revenue: ${total_revenue:,.2f}"
        )

        print(
            f"Total Profit: ${total_profit:,.2f}"
        )


# ---------------------------------------------------------
# Business event verification
# ---------------------------------------------------------

def verify_europe_q3_event():

    query = text(
        """
        SELECT
            quarter,
            ROUND(
                SUM(profit) / SUM(revenue) * 100,
                2
            ) AS profit_margin
        FROM sales
        WHERE region = 'Europe'
          AND year = 2026
          AND quarter IN ('Q2', 'Q3')
        GROUP BY quarter
        ORDER BY quarter
        """
    )

    with engine.connect() as connection:

        result = connection.execute(query)

        rows = result.fetchall()

    print("\nEuropean Margin Comparison - 2026")

    for row in rows:
        print(
            f"{row.quarter}: {row.profit_margin}%"
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    load_sales_data()

    verify_database()

    verify_europe_q3_event()