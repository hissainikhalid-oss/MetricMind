import re
from typing import Dict, Any

from sqlalchemy import text

try:
    from .database import get_engine
    from .query_engine import QueryEngine
except ImportError:
    from database import get_engine
    from query_engine import QueryEngine


class AnalysisEngine:

    def __init__(self):

        self.engine = get_engine()
        self.query_engine = QueryEngine()


    # -----------------------------------------------------
    # Quarter helpers
    # -----------------------------------------------------

    def previous_quarter(
        self,
        year: int,
        quarter: str
    ):

        quarter_number = int(
            quarter.replace("Q", "")
        )

        if quarter_number == 1:

            return year - 1, "Q4"

        return (
            year,
            f"Q{quarter_number - 1}"
        )


    # -----------------------------------------------------
    # Extract year / quarter / region
    # -----------------------------------------------------

    def detect_context(
        self,
        question: str
    ) -> Dict[str, Any]:

        filters = (
            self.query_engine
            .detect_filters(question)
        )

        if "region" not in filters:

            raise ValueError(
                "Please specify a region."
            )

        if "year" not in filters:

            raise ValueError(
                "Please specify a year."
            )

        if "quarter" not in filters:

            raise ValueError(
                "Please specify a quarter."
            )

        return filters


    # -----------------------------------------------------
    # Query period metrics
    # -----------------------------------------------------

    def get_period_metrics(
        self,
        region: str,
        year: int,
        quarter: str
    ) -> Dict[str, float]:

        query = text(
            """
            SELECT
                SUM(revenue) AS revenue,
                SUM(material_cost) AS material_cost,
                SUM(shipping_cost) AS shipping_cost,
                SUM(operating_cost) AS operating_cost,
                SUM(total_cost) AS total_cost,
                SUM(profit) AS profit,

                (
                    SUM(profit)
                    / NULLIF(SUM(revenue), 0)
                ) * 100 AS profit_margin

            FROM sales

            WHERE region = :region
              AND year = :year
              AND quarter = :quarter
            """
        )

        with self.engine.connect() as connection:

            row = connection.execute(
                query,
                {
                    "region": region,
                    "year": year,
                    "quarter": quarter
                }
            ).mappings().first()

        if not row or row["revenue"] is None:

            raise ValueError(
                "No data found for the requested period."
            )

        revenue = float(row["revenue"])

        return {

            "revenue":
                revenue,

            "material_cost":
                float(row["material_cost"]),

            "shipping_cost":
                float(row["shipping_cost"]),

            "operating_cost":
                float(row["operating_cost"]),

            "total_cost":
                float(row["total_cost"]),

            "profit":
                float(row["profit"]),

            "profit_margin":
                float(row["profit_margin"]),

            "material_cost_ratio":
                (
                    float(row["material_cost"])
                    / revenue
                    * 100
                ),

            "shipping_cost_ratio":
                (
                    float(row["shipping_cost"])
                    / revenue
                    * 100
                ),

            "operating_cost_ratio":
                (
                    float(row["operating_cost"])
                    / revenue
                    * 100
                )
        }


    # -----------------------------------------------------
    # Root-cause analysis
    # -----------------------------------------------------

    def analyze_margin_change(
        self,
        question: str
    ) -> Dict[str, Any]:

        context = self.detect_context(
            question
        )

        region = context["region"]
        year = context["year"]
        quarter = context["quarter"]

        previous_year, previous_q = (
            self.previous_quarter(
                year,
                quarter
            )
        )

        current = self.get_period_metrics(
            region,
            year,
            quarter
        )

        previous = self.get_period_metrics(
            region,
            previous_year,
            previous_q
        )

        margin_change = (
            current["profit_margin"]
            - previous["profit_margin"]
        )

        revenue_change_pct = (
            (
                current["revenue"]
                - previous["revenue"]
            )
            / previous["revenue"]
            * 100
        )

        cost_drivers = {

            "Material Cost": (
                current["material_cost_ratio"]
                - previous["material_cost_ratio"]
            ),

            "Shipping Cost": (
                current["shipping_cost_ratio"]
                - previous["shipping_cost_ratio"]
            ),

            "Operating Cost": (
                current["operating_cost_ratio"]
                - previous["operating_cost_ratio"]
            )
        }

        ranked_drivers = sorted(
            cost_drivers.items(),
            key=lambda item: item[1],
            reverse=True
        )

        primary_driver = ranked_drivers[0]

        explanation = self.build_explanation(
            region=region,
            year=year,
            quarter=quarter,
            previous_year=previous_year,
            previous_quarter=previous_q,
            current=current,
            previous=previous,
            margin_change=margin_change,
            revenue_change_pct=revenue_change_pct,
            ranked_drivers=ranked_drivers
        )

        return {

            "success": True,

            "question": question,

            "region": region,

            "current_period": {
                "year": year,
                "quarter": quarter
            },

            "comparison_period": {
                "year": previous_year,
                "quarter": previous_q
            },

            "previous_margin":
                previous["profit_margin"],

            "current_margin":
                current["profit_margin"],

            "margin_change_percentage_points":
                margin_change,

            "revenue_change_percent":
                revenue_change_pct,

            "cost_drivers": [
                {
                    "name": name,
                    "change_percentage_points": change
                }
                for name, change
                in ranked_drivers
            ],

            "primary_driver":
                primary_driver[0],

            "explanation":
                explanation,

            "governed": True
        }


    # -----------------------------------------------------
    # Build deterministic explanation
    # -----------------------------------------------------

    def build_explanation(
        self,
        region,
        year,
        quarter,
        previous_year,
        previous_quarter,
        current,
        previous,
        margin_change,
        revenue_change_pct,
        ranked_drivers
    ):

        direction = (
            "fell"
            if margin_change < 0
            else "increased"
        )

        strongest_drivers = [
            driver
            for driver in ranked_drivers
            if driver[1] > 0
        ]

        driver_sentences = []

        for name, change in strongest_drivers:

            driver_sentences.append(
                f"{name} increased by "
                f"{change:.2f} percentage points "
                f"as a share of revenue"
            )

        if driver_sentences:

            drivers_text = "; ".join(
                driver_sentences
            )

        else:

            drivers_text = (
                "no major cost-ratio increase "
                "was detected"
            )

        explanation = (
            f"{region}'s profit margin {direction} "
            f"from "
            f"{previous['profit_margin']:.2f}% "
            f"in {previous_quarter} {previous_year} "
            f"to "
            f"{current['profit_margin']:.2f}% "
            f"in {quarter} {year}, "
            f"a change of "
            f"{margin_change:.2f} percentage points. "
            f"{drivers_text}. "
            f"Revenue changed by "
            f"{revenue_change_pct:.2f}% "
            f"between the two periods."
        )

        return explanation


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    engine = AnalysisEngine()

    question = (
        "Why did European profit margin "
        "drop in Q3 2026?"
    )

    print("=" * 70)
    print("METRICMIND ROOT-CAUSE ANALYSIS")
    print("=" * 70)

    print(
        f"\nQUESTION: {question}"
    )

    result = (
        engine.analyze_margin_change(
            question
        )
    )

    print(
        f"\nPrevious Margin: "
        f"{result['previous_margin']:.2f}%"
    )

    print(
        f"Current Margin: "
        f"{result['current_margin']:.2f}%"
    )

    print(
        f"Margin Change: "
        f"{result['margin_change_percentage_points']:.2f} "
        f"percentage points"
    )

    print(
        f"\nPrimary Driver: "
        f"{result['primary_driver']}"
    )

    print("\nCost Drivers:")

    for driver in result["cost_drivers"]:

        print(
            f"- {driver['name']}: "
            f"{driver['change_percentage_points']:.2f} pp"
        )

    print("\nANALYSIS:")

    print(
        result["explanation"]
    )

    print(
        "\nGOVERNED: True"
    )