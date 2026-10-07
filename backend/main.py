from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .query_engine import QueryEngine
    from .analysis_engine import AnalysisEngine
    from .semantic_engine import SemanticEngine
    from .audit_service import AuditService
except ImportError:
    from query_engine import QueryEngine
    from analysis_engine import AnalysisEngine
    from semantic_engine import SemanticEngine
    from audit_service import AuditService

# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

app = FastAPI(
    title="MetricMind API",
    description=(
        "Governed Semantic Business Intelligence API "
        "for reliable conversational analytics."
    ),
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Engines
# ---------------------------------------------------------

query_engine = QueryEngine()
analysis_engine = AnalysisEngine()
semantic_engine = SemanticEngine()
audit_service = AuditService()


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=3,
        description="Natural-language business question"
    )


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "application": "MetricMind",
        "status": "running",
        "version": "1.0.0",
        "description": (
            "Agentic Semantic BI Engine"
        )
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "semantic_model": (
            semantic_engine.get_model_name()
        ),
        "warehouse_table": (
            semantic_engine.get_table_name()
        )
    }


# ---------------------------------------------------------
# Semantic metadata
# ---------------------------------------------------------

@app.get("/api/metrics")
def get_metrics():

    output = []

    for metric_name in (
        semantic_engine.list_metrics()
    ):

        info = (
            semantic_engine
            .metric_governance_info(
                metric_name
            )
        )

        output.append(info)

    return {
        "count": len(output),
        "metrics": output
    }


@app.get("/api/dimensions")
def get_dimensions():

    dimensions = []

    for dimension_name in (
        semantic_engine.list_dimensions()
    ):

        dimension = (
            semantic_engine
            .get_dimension(
                dimension_name
            )
        )

        dimensions.append({
            "name": dimension_name,
            **dimension
        })

    return {
        "count": len(dimensions),
        "dimensions": dimensions
    }


# ---------------------------------------------------------
# Standard governed query
# ---------------------------------------------------------

@app.post("/api/query")
def governed_query(
    request: QuestionRequest
):

    try:

        result = query_engine.ask(
            request.question
        )

        if not result["success"]:

            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ---------------------------------------------------------
# Root-cause analysis
# ---------------------------------------------------------

@app.post("/api/analyze")
def root_cause_analysis(
    request: QuestionRequest
):

    try:

        return (
            analysis_engine
            .analyze_margin_change(
                request.question
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

@app.get("/api/audit")
def get_audit_history(
    limit: int = 50
):

    limit = max(
        1,
        min(limit, 200)
    )

    history = audit_service.get_history(
        limit
    )

    return {
        "count": len(history),
        "history": history
    }
# ---------------------------------------------------------
# Unified conversational endpoint
# ---------------------------------------------------------

@app.post("/api/ask")
def ask_metricmind(
    request: QuestionRequest
):

    question = (
        request.question
        .lower()
        .strip()
    )

    try:

        # Root-cause / diagnostic intent
        analysis_words = [
            "why",
            "reason",
            "cause",
            "caused",
            "driver",
            "drivers"
        ]

        is_analysis = any(
            word in question
            for word in analysis_words
        )

        # -------------------------------------------------
        # Root-cause analysis
        # -------------------------------------------------

        if (
            is_analysis
            and "margin" in question
        ):

            result = (
                analysis_engine
                .analyze_margin_change(
                    request.question
                )
            )

            # Save query to audit history
            audit_service.log(
                question=request.question,
                mode="root_cause_analysis",
                metric="profit_margin",
                filters={
                    "region":
                        result["region"],

                    "year":
                        result[
                            "current_period"
                        ]["year"],

                    "quarter":
                        result[
                            "current_period"
                        ]["quarter"]
                },
                generated_query=(
                    "Governed period comparison "
                    "and cost-driver analysis"
                ),
                governed=True
            )

            return {
                "mode": "root_cause_analysis",
                **result
            }

        # -------------------------------------------------
        # Standard governed BI query
        # -------------------------------------------------

        result = query_engine.ask(
            request.question
        )

        if not result["success"]:

            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )

        # Save query to audit history
        audit_service.log(
            question=request.question,
            mode="governed_query",
            metric=result["metric"],
            filters=result["filters"],
            generated_query=result["query"],
            governed=True
        )

        return {
            "mode": "governed_query",
            **result
        }

    except HTTPException:
        raise

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )