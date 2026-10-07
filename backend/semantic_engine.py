from pathlib import Path
from typing import Dict, Any, List

import yaml


BASE_DIR = Path(__file__).resolve().parent.parent

SEMANTIC_FILE = (
    BASE_DIR
    / "semantic"
    / "metrics.yaml"
)


class SemanticEngine:

    def __init__(self):

        self.schema = self._load_schema()

        self.model = self.schema["model"]

        self.metrics = self.schema["metrics"]

        self.dimensions = self.schema["dimensions"]


    # -----------------------------------------------------
    # Load semantic YAML
    # -----------------------------------------------------

    def _load_schema(self) -> Dict[str, Any]:

        if not SEMANTIC_FILE.exists():

            raise FileNotFoundError(
                f"Semantic model not found: {SEMANTIC_FILE}"
            )

        with open(
            SEMANTIC_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            schema = yaml.safe_load(file)

        required_sections = [
            "model",
            "metrics",
            "dimensions"
        ]

        for section in required_sections:

            if section not in schema:

                raise ValueError(
                    f"Missing semantic section: {section}"
                )

        return schema


    # -----------------------------------------------------
    # Model information
    # -----------------------------------------------------

    def get_table_name(self) -> str:

        return self.model["table"]


    def get_model_name(self) -> str:

        return self.model["name"]


    # -----------------------------------------------------
    # Metric functions
    # -----------------------------------------------------

    def list_metrics(self) -> List[str]:

        return list(self.metrics.keys())


    def get_metric(
        self,
        metric_name: str
    ) -> Dict[str, Any]:

        if metric_name not in self.metrics:

            raise ValueError(
                f"Unknown governed metric: {metric_name}"
            )

        return self.metrics[metric_name]


    def get_metric_expression(
        self,
        metric_name: str
    ) -> str:

        metric = self.get_metric(metric_name)

        return metric["expression"]


    # -----------------------------------------------------
    # Dimension functions
    # -----------------------------------------------------

    def list_dimensions(self) -> List[str]:

        return list(self.dimensions.keys())


    def get_dimension(
        self,
        dimension_name: str
    ) -> Dict[str, Any]:

        if dimension_name not in self.dimensions:

            raise ValueError(
                f"Unknown dimension: {dimension_name}"
            )

        return self.dimensions[dimension_name]


    # -----------------------------------------------------
    # Metric matching
    # -----------------------------------------------------

    def find_metric(
        self,
        user_text: str
    ):

        text = user_text.lower().strip()

        candidates = []

        # Collect aliases and readable metric names
        for metric_name, metric in self.metrics.items():

            aliases = metric.get(
                "aliases",
                []
            )

            for alias in aliases:

                candidates.append(
                    (
                        alias.lower(),
                        metric_name
                    )
                )

            readable_name = (
                metric_name
                .replace("_", " ")
                .lower()
            )

            candidates.append(
                (
                    readable_name,
                    metric_name
                )
            )
        

        # Check longer / more specific phrases first
        candidates.sort(
            key=lambda item: len(item[0]),
            reverse=True
        )

        for phrase, metric_name in candidates:

            if phrase in text:

                return metric_name

        return None


    # -----------------------------------------------------
    # Governance information
    # -----------------------------------------------------

    def metric_governance_info(
        self,
        metric_name: str
    ) -> Dict[str, Any]:

        metric = self.get_metric(metric_name)

        return {
            "metric": metric_name,
            "label": metric["label"],
            "definition": metric["expression"],
            "format": metric["format"],
            "description": metric["description"],
            "governed": True
        }


# ---------------------------------------------------------
# Test semantic engine
# ---------------------------------------------------------

if __name__ == "__main__":

    engine = SemanticEngine()

    print("=" * 60)
    print("METRICMIND SEMANTIC LAYER")
    print("=" * 60)

    print(
        f"\nModel: {engine.get_model_name()}"
    )

    print(
        f"Database table: {engine.get_table_name()}"
    )

    print("\nGoverned Metrics:")

    for metric_name in engine.list_metrics():

        metric = engine.get_metric(
            metric_name
        )

        print(
            f"- {metric_name}: "
            f"{metric['expression']}"
        )

    print("\nDimensions:")

    for dimension in engine.list_dimensions():

        print(
            f"- {dimension}"
        )

    print("\nMetric Detection Tests:")

    questions = [
        "What is our total revenue?",
        "What is our profit margin?",
        "How much did we spend on shipping?",
        "How many orders do we have?"
    ]

    for question in questions:

        metric = engine.find_metric(
            question
        )

        print(
            f"{question}"
        )

        print(
            f"  -> {metric}"
        )