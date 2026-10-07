import json
from datetime import datetime, timezone

from sqlalchemy import text

try:
    from .database import get_engine
except ImportError:
    from database import get_engine


class AuditService:

    def __init__(self):

        self.engine = get_engine()

        self.create_table()


    # -----------------------------------------------------
    # Create audit table
    # -----------------------------------------------------

    def create_table(self):

        query = text(
            """
            CREATE TABLE IF NOT EXISTS query_audit (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                question TEXT NOT NULL,

                mode TEXT NOT NULL,

                metric TEXT,

                filters TEXT,

                generated_query TEXT,

                governed INTEGER NOT NULL,

                created_at TEXT NOT NULL
            )
            """
        )

        with self.engine.begin() as connection:

            connection.execute(query)


    # -----------------------------------------------------
    # Record query
    # -----------------------------------------------------

    def log(
        self,
        question,
        mode,
        metric=None,
        filters=None,
        generated_query=None,
        governed=True
    ):

        query = text(
            """
            INSERT INTO query_audit
            (
                question,
                mode,
                metric,
                filters,
                generated_query,
                governed,
                created_at
            )
            VALUES
            (
                :question,
                :mode,
                :metric,
                :filters,
                :generated_query,
                :governed,
                :created_at
            )
            """
        )

        values = {

            "question":
                question,

            "mode":
                mode,

            "metric":
                metric,

            "filters":
                json.dumps(
                    filters or {}
                ),

            "generated_query":
                generated_query,

            "governed":
                1 if governed else 0,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        with self.engine.begin() as connection:

            connection.execute(
                query,
                values
            )


    # -----------------------------------------------------
    # Retrieve audit history
    # -----------------------------------------------------

    def get_history(
        self,
        limit=50
    ):

        query = text(
            """
            SELECT
                id,
                question,
                mode,
                metric,
                filters,
                generated_query,
                governed,
                created_at

            FROM query_audit

            ORDER BY id DESC

            LIMIT :limit
            """
        )

        with self.engine.connect() as connection:

            rows = connection.execute(
                query,
                {
                    "limit": limit
                }
            ).mappings().all()

        history = []

        for row in rows:

            history.append({

                "id":
                    row["id"],

                "question":
                    row["question"],

                "mode":
                    row["mode"],

                "metric":
                    row["metric"],

                "filters":
                    json.loads(
                        row["filters"]
                    ),

                "generated_query":
                    row["generated_query"],

                "governed":
                    bool(
                        row["governed"]
                    ),

                "created_at":
                    row["created_at"]
            })

        return history


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    service = AuditService()

    service.log(
        question="Test governed query",
        mode="governed_query",
        metric="total_revenue",
        filters={
            "region": "Europe"
        },
        generated_query=(
            "SELECT SUM(revenue) FROM sales"
        ),
        governed=True
    )

    history = service.get_history()

    print("=" * 60)
    print("METRICMIND QUERY AUDIT")
    print("=" * 60)

    for item in history:

        print(
            f"\nID: {item['id']}"
        )

        print(
            f"Question: {item['question']}"
        )

        print(
            f"Mode: {item['mode']}"
        )

        print(
            f"Governed: {item['governed']}"
        )