import re
from typing import Dict, Any, Optional, List

from sqlalchemy import text

try:
    from .database import get_engine
    from .semantic_engine import SemanticEngine
except ImportError:
    from database import get_engine
    from semantic_engine import SemanticEngine


class QueryEngine:

    def __init__(self):

        self.semantic = SemanticEngine()
        self.engine = get_engine()

        self.region_aliases = {
            "europe": "Europe",
            "european": "Europe",

            "north america": "North America",
            "north american": "North America",

            "asia pacific": "Asia Pacific",
            "apac": "Asia Pacific",
            "asian pacific": "Asia Pacific",

            "middle east": "Middle East",
            "middle eastern": "Middle East",
        }


    # -----------------------------------------------------
    # Detect filters from natural language
    # -----------------------------------------------------

    def detect_filters(
        self,
        question: str
    ) -> Dict[str, Any]:

        question_lower = question.lower()

        filters = {}

        # Region
        for phrase, region in self.region_aliases.items():

            if phrase in question_lower:

                filters["region"] = region
                break

        # Year
        year_match = re.search(
            r"\b(20\d{2})\b",
            question_lower
        )

        if year_match:
            filters["year"] = int(
                year_match.group(1)
            )

        # Quarter
        quarter_match = re.search(
            r"\bq([1-4])\b",
            question_lower
        )

        if quarter_match:
            filters["quarter"] = (
                f"Q{quarter_match.group(1)}"
            )

        return filters


    # -----------------------------------------------------
    # Detect grouping
    # -----------------------------------------------------

    def detect_group_by(
        self,
        question: str
    ) -> Optional[str]:

        question_lower = question.lower()

        mappings = {
            "by region": "region",
            "by country": "country",
            "by category": "category",
            "by product": "product",
            "by quarter": "quarter",
            "by year": "year",
            "by month": "month",
        }

        for phrase, dimension in mappings.items():

            if phrase in question_lower:
                return dimension

        return None


    # -----------------------------------------------------
    # Build governed query
    # -----------------------------------------------------

    def build_query(
        self,
        metric_name: str,
        filters: Optional[Dict[str, Any]] = None,
        group_by: Optional[str] = None
    ):

        metric_expression = (
            self.semantic
            .get_metric_expression(metric_name)
        )

        table_name = (
            self.semantic
            .get_table_name()
        )

        params = {}

        if group_by:

            dimension = (
                self.semantic
                .get_dimension(group_by)
            )

            dimension_column = dimension["column"]

            select_clause = (
                f"{dimension_column} AS dimension, "
                f"{metric_expression} AS value"
            )

        else:

            select_clause = (
                f"{metric_expression} AS value"
            )

        sql = f"""
        SELECT
            {select_clause}
        FROM {table_name}
        """

        where_conditions = []

        if filters:

            for filter_name, filter_value in filters.items():

                dimension = (
                    self.semantic
                    .get_dimension(filter_name)
                )

                column = dimension["column"]

                parameter_name = (
                    f"filter_{filter_name}"
                )

                where_conditions.append(
                    f"{column} = :{parameter_name}"
                )

                params[parameter_name] = filter_value

        if where_conditions:

            sql += "\nWHERE "

            sql += " AND ".join(
                where_conditions
            )

        if group_by:

            sql += (
                f"\nGROUP BY {dimension_column}"
            )

            sql += (
                "\nORDER BY value DESC"
            )

        return text(sql), params


    # -----------------------------------------------------
    # Execute query
    # -----------------------------------------------------

    def execute_query(
        self,
        metric_name: str,
        filters: Optional[Dict[str, Any]] = None,
        group_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        query, params = self.build_query(
            metric_name=metric_name,
            filters=filters,
            group_by=group_by
        )

        with self.engine.connect() as connection:

            result = connection.execute(
                query,
                params
            )

            rows = result.fetchall()

        output = []

        for row in rows:

            if group_by:

                output.append({
                    "dimension": row.dimension,
                    "value": row.value
                })

            else:

                output.append({
                    "value": row.value
                })

        return output


    # -----------------------------------------------------
    # Format values
    # -----------------------------------------------------

    def format_value(
        self,
        metric_name: str,
        value
    ) -> str:

        metric = (
            self.semantic
            .get_metric(metric_name)
        )

        metric_format = metric.get(
            "format",
            "number"
        )

        if value is None:
            return "No data"

        if metric_format == "currency":

            return f"${value:,.2f}"

        if metric_format == "percentage":

            return f"{value:.2f}%"

        if metric_format == "integer":

            return f"{int(value):,}"

        return f"{value:,.2f}"

    # -----------------------------------------------------
    # Build conversational answer
    # -----------------------------------------------------

    def build_answer(
        self,
        metric_name: str,
        filters: Dict[str, Any],
        group_by: Optional[str],
        results: List[Dict[str, Any]]
    ) -> str:

        metric = self.semantic.get_metric(
            metric_name
        )

        label = metric["label"]

        if group_by:

            if not results:
                return f"No data was found for {label}."

            top_result = results[0]

            return (
                f"{top_result['dimension']} has the highest "
                f"{label.lower()} at "
                f"{self.format_value(metric_name, top_result['value'])}."
            )

        if not results:
            return f"No data was found for {label}."

        value = self.format_value(
            metric_name,
            results[0]["value"]
        )

        context_parts = []

        if "region" in filters:
            context_parts.append(filters["region"])

        if "quarter" in filters:
            context_parts.append(filters["quarter"])

        if "year" in filters:
            context_parts.append(str(filters["year"]))

        if context_parts:

            context = " ".join(
                str(item)
                for item in context_parts
            )

            return (
                f"{label} for {context} was {value}."
            )

        return f"{label} was {value}."

    # -----------------------------------------------------
    # Natural-language query interface
    # -----------------------------------------------------

    def ask(
        self,
        question: str
    ) -> Dict[str, Any]:

        metric_name = (
            self.semantic
            .find_metric(question)
        )

        if not metric_name:

            return {
                "success": False,
                "question": question,
                "error": (
                    "No governed metric could "
                    "be identified."
                )
            }

        filters = self.detect_filters(
            question
        )

        group_by = self.detect_group_by(
            question
        )

        query, params = self.build_query(
            metric_name=metric_name,
            filters=filters,
            group_by=group_by
        )

        results = self.execute_query(
            metric_name=metric_name,
            filters=filters,
            group_by=group_by
        )

        formatted_results = []

        for item in results:

            formatted_item = dict(item)

            formatted_item["formatted_value"] = (
                self.format_value(
                    metric_name,
                    item["value"]
                )
            )

            formatted_results.append(
                formatted_item
            )

        governance = (
            self.semantic
            .metric_governance_info(
                metric_name
            )
        )
        answer = self.build_answer(
            metric_name=metric_name,
            filters=filters,
            group_by=group_by,
            results=results
        )

        return {
            "success": True,

            "question": question,

            "answer": answer,

            "metric": metric_name,

            "metric_label": governance["label"],

            "metric_definition": (
                governance["definition"]
            ),

            "governed": True,

            "filters": filters,

            "group_by": group_by,

            "query": str(query),

            "parameters": params,

            "results": formatted_results
        }


# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    query_engine = QueryEngine()

    questions = [
        "What is our total revenue?",

        "What is our profit margin?",

        "What was European revenue in Q3 2026?",

        "What was European profit margin in Q3 2026?",

        "Show revenue by region",
    ]

    print("=" * 70)
    print("METRICMIND GOVERNED QUERY ENGINE")
    print("=" * 70)

    for question in questions:

        print("\n" + "-" * 70)

        print(
            f"QUESTION: {question}"
        )

        response = query_engine.ask(
            question
        )

        if not response["success"]:

            print(
                f"ERROR: {response['error']}"
            )

            continue

        print(
            f"METRIC: "
            f"{response['metric']}"
        )

        print(
            f"FILTERS: "
            f"{response['filters']}"
        )

        print(
            f"GROUP BY: "
            f"{response['group_by']}"
        )

        print(
            "GOVERNED: True"
        )

        print("RESULT:")

        for result in response["results"]:

            if response["group_by"]:

                print(
                    f"  {result['dimension']}: "
                    f"{result['formatted_value']}"
                )

            else:

                print(
                    f"  {result['formatted_value']}"
                )