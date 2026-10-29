from pathlib import Path

import pandas as pd

from chatbot.data_service import search_plants


class PlantAgent:
    name = "PlantAgent"

    def run(self, query="", data_type="benefits"):
        result = search_plants(
            query=query,
            data_type=data_type,
            limit=20,
        )

        return {
            "agent": self.name,
            "question": query,
            "data_type": data_type,
            "total_results": result["total_results"],
            "results": result["results"],
        }


class VegetationAgent:
    name = "VegetationAgent"

    def run(self, query=""):
        result = search_plants(
            query=query,
            data_type="distribution",
            limit=20,
        )

        return {
            "agent": self.name,
            "question": query,
            "description": "Search vegetation distribution records",
            "total_results": result["total_results"],
            "results": result["results"],
        }


class TrendAgent:
    name = "TrendAgent"

    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        self.csv_path = project_root / "data" / "region_year_metrics.csv"

    def run(self, query="", region_id=None, year=None):
        if not self.csv_path.exists():
            return {
                "agent": self.name,
                "status": "error",
                "message": "The region_year_metrics.csv file was not found.",
            }

        try:
            df = pd.read_csv(self.csv_path)

            required_columns = {
                "region_id",
                "year",
                "ndvi_mean",
                "density_score",
                "is_forecast",
            }

            missing_columns = required_columns - set(df.columns)

            if missing_columns:
                return {
                    "agent": self.name,
                    "status": "error",
                    "message": "Required columns are missing.",
                    "missing_columns": sorted(missing_columns),
                }

            # Convert relevant columns to numeric values.
            for column in [
                "region_id",
                "year",
                "ndvi_mean",
                "density_score",
                "is_forecast",
            ]:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                )

            df = df.dropna(
                subset=[
                    "region_id",
                    "year",
                    "ndvi_mean",
                    "density_score",
                    "is_forecast",
                ]
            )

            # Exclude forecast records from historical measurements.
            historical = df[df["is_forecast"] == 0].copy()
            forecasts = df[df["is_forecast"] == 1].copy()

            # Optional region filter.
            if region_id is not None:
                historical = historical[
                    historical["region_id"] == int(region_id)
                ]
                forecasts = forecasts[
                    forecasts["region_id"] == int(region_id)
                ]

            if historical.empty:
                return {
                    "agent": self.name,
                    "status": "no_data",
                    "question": query,
                    "message": "No historical measurements were found.",
                    "region_id": region_id,
                }

            # Summarize each year across the selected regions.
            yearly = (
                historical.groupby("year")
                .agg(
                    region_count=("region_id", "nunique"),
                    ndvi_mean=("ndvi_mean", "mean"),
                    density_score=("density_score", "mean"),
                )
                .reset_index()
                .sort_values("year")
            )

            # Optional specific year.
            selected_year = None

            if year is not None:
                selected_year = int(year)
                matching_year = yearly[yearly["year"] == selected_year]

                if matching_year.empty:
                    return {
                        "agent": self.name,
                        "status": "no_data",
                        "question": query,
                        "message": (
                            f"No historical measurements were found "
                            f"for year {selected_year}."
                        ),
                        "region_id": region_id,
                    }

                selected_year = matching_year.iloc[0].to_dict()

            first = yearly.iloc[0]
            last = yearly.iloc[-1]

            ndvi_change = round(
                float(last["ndvi_mean"] - first["ndvi_mean"]),
                4,
            )

            density_change = round(
                float(last["density_score"] - first["density_score"]),
                2,
            )

            if ndvi_change > 0:
                overall_trend = "increasing"
            elif ndvi_change < 0:
                overall_trend = "decreasing"
            else:
                overall_trend = "stable"

            forecast_summary = None

            if not forecasts.empty:
                forecast_yearly = (
                    forecasts.groupby("year")
                    .agg(
                        region_count=("region_id", "nunique"),
                        ndvi_mean=("ndvi_mean", "mean"),
                        density_score=("density_score", "mean"),
                    )
                    .reset_index()
                    .sort_values("year")
                )

                forecast_summary = {
                    "record_count": int(len(forecasts)),
                    "yearly_data": forecast_yearly.round(4)
                    .to_dict(orient="records"),
                }

            return {
                "agent": self.name,
                "status": "success",
                "question": query,
                "region_id": region_id,
                "historical_summary": {
                    "record_count": int(len(historical)),
                    "start_year": int(first["year"]),
                    "end_year": int(last["year"]),
                    "yearly_data": yearly.round(4).to_dict(
                        orient="records"
                    ),
                    "overall_trend": overall_trend,
                    "ndvi_change": ndvi_change,
                    "density_change": density_change,
                },
                "selected_year": selected_year,
                "forecasts": forecast_summary,
            }

        except (ValueError, TypeError) as error:
            return {
                "agent": self.name,
                "status": "error",
                "message": str(error),
            }
        except Exception as error:
            return {
                "agent": self.name,
                "status": "error",
                "message": f"Unable to analyze vegetation trends: {error}",
            }
