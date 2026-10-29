from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

from chatbot.data_service import search_plants

mcp = FastMCP("Vegetation Intelligence Assistant")

METRICS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "region_year_metrics.csv"
)


@mcp.tool()
def search_plant_data(
    query: str = "",
    data_type: str = "distribution"
) -> dict:
    """
    Search Saudi Arabian plant datasets.

    data_type options:
    distribution, rare, toxic, benefits.
    """
    allowed_types = ["distribution", "rare", "toxic", "benefits"]

    if data_type not in allowed_types:
        return {
            "error": "Unsupported data type",
            "allowed_types": allowed_types,
        }

    try:
        return search_plants(
            query=query,
            data_type=data_type,
            limit=20,
        )
    except Exception as error:
        return {"error": str(error)}


@mcp.tool()
def get_plant_dataset_summary() -> dict:
    """Get record counts for the available plant datasets."""
    summary = {}

    for data_type in ["distribution", "rare", "toxic", "benefits"]:
        try:
            result = search_plants(
                query="",
                data_type=data_type,
                limit=1,
            )
            summary[data_type] = result["total_results"]
        except Exception as error:
            summary[data_type] = {"error": str(error)}

    return summary


@mcp.tool()

def analyze_vegetation_trends(
    region_id: int = 0,
    start_year: int = 0,
    end_year: int = 0,
    include_forecasts: bool = False,
) -> dict:
    """
    Analyze historical vegetation measurements and future forecasts
    from region_year_metrics.csv.

    region_id=0 means all regions.
    start_year=0 and end_year=0 mean no year boundary.
    Forecasts are returned separately when include_forecasts=True.
    """
    if not METRICS_FILE.exists():
        return {
            "success": False,
            "error": "region_year_metrics.csv was not found.",
        }

    try:
        df = pd.read_csv(METRICS_FILE)

        required_columns = {
            "region_id",
            "year",
            "ndvi_mean",
            "density_score",
            "is_forecast",
        }

        missing = required_columns - set(df.columns)
        if missing:
            return {
                "success": False,
                "error": "Required columns are missing.",
                "missing_columns": sorted(missing),
            }

        for column in required_columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df = df.dropna(
            subset=[
                "region_id",
                "year",
                "ndvi_mean",
                "density_score",
                "is_forecast",
            ]
        )

        if region_id < 0:
            return {
                "success": False,
                "error": "region_id must be 0 or a positive integer.",
            }

        if start_year and end_year and start_year > end_year:
            return {
                "success": False,
                "error": "start_year cannot be greater than end_year.",
            }

        # Apply region and year filters first.
        if region_id:
            df = df[df["region_id"] == region_id]

        if start_year:
            df = df[df["year"] >= start_year]

        if end_year:
            df = df[df["year"] <= end_year]

        # Split historical measurements from forecasts.
        historical = df[df["is_forecast"] == 0].copy()
        forecasts = df[df["is_forecast"] == 1].copy()

        def summarize(data):
            if data.empty:
                return {
                    "record_count": 0,
                    "yearly_data": [],
                    "summary": None,
                }

            yearly = (
                data.groupby("year")
                .agg(
                    region_count=("region_id", "nunique"),
                    record_count=("region_id", "size"),
                    ndvi_mean=("ndvi_mean", "mean"),
                    density_score=("density_score", "mean"),
                )
                .reset_index()
                .sort_values("year")
            )

            yearly["year"] = yearly["year"].astype(int)
            yearly["region_count"] = yearly["region_count"].astype(int)
            yearly["record_count"] = yearly["record_count"].astype(int)

            yearly_data = yearly.round(
                {"ndvi_mean": 4, "density_score": 2}
            ).to_dict(orient="records")

            first = yearly.iloc[0]
            last = yearly.iloc[-1]

            ndvi_change = float(last["ndvi_mean"] - first["ndvi_mean"])
            density_change = float(
                last["density_score"] - first["density_score"]
            )

            if ndvi_change > 0:
                trend = "increasing"
            elif ndvi_change < 0:
                trend = "decreasing"
            else:
                trend = "stable"

            return {
                "record_count": int(len(data)),
                "yearly_data": yearly_data,
                "summary": {
                    "first_year": int(first["year"]),
                    "last_year": int(last["year"]),
                    "ndvi_change": round(ndvi_change, 4),
                    "density_change": round(density_change, 2),
                    "ndvi_trend": trend,
                },
            }

        historical_result = summarize(historical)

        result = {
            "success": True,
            "source": "region_year_metrics.csv",
            "filters": {
                "region_id": region_id or None,
                "start_year": start_year or None,
                "end_year": end_year or None,
                "include_forecasts": include_forecasts,
            },
            "historical": historical_result,
        }

        if include_forecasts:
            result["forecasts"] = summarize(forecasts)

        result["record_count"] = (
            historical_result["record_count"]
            + (len(forecasts) if include_forecasts else 0)
        )

        return result

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }
@mcp.resource("vegetation://datasets")
def get_vegetation_datasets_resource() -> str:
    """Describe the vegetation datasets available to the assistant."""
    return (
        "Available datasets:\n"
        "1. Plant distribution data.\n"
        "2. Rare plant data.\n"
        "3. Toxic plant data.\n"
        "4. Beneficial plant data.\n"
        "5. Historical vegetation metrics and forecasts from "
        "region_year_metrics.csv.\n"
        "Use the MCP tools to search and analyze the available data."
    )


@mcp.prompt()
def vegetation_research_prompt(question: str) -> str:
    """Create a research prompt for questions about Saudi vegetation."""
    return (
        "You are a vegetation research assistant specializing in "
        "Saudi Arabia.\n"
        "Answer the following question using the available datasets "
        "and tools.\n"
        "Distinguish historical measurements from forecasts, "
        "and do not present forecasts as verified observations.\n"
        f"Question: {question}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")