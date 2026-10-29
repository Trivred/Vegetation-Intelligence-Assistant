import re

from chatbot.mcp_client import run_mcp_tool


class Supervisor:
    """Rule-based Supervisor connected to MCP tools."""

    def route(self, question: str) -> dict:
        question = question.strip()

        if not question:
            return {
                "success": False,
                "message": "Please enter a question.",
                "agent": None,
            }

        text = question.casefold()

        # 1. Route historical analysis and forecasts to the MCP trend tool.
        trend_keywords = [
            "trend",
            "historical",
            "change over time",
            "over the years",
            "forecast",
            "prediction",
            "predict",
            "ndvi",
            "density score",
            "vegetation analysis",
            "analyze vegetation",
            "analyse vegetation",
            "تغير",
            "التغير",
            "اتجاه",
            "زمني",
            "سنوات",
            "السنة",
            "عام",
            "تاريخي",
            "تاريخية",
            "توقعات",
            "توقع",
            "كثافة الغطاء",
            "تحليل الغطاء",
            "تحليل النباتات",
            "الغطاء النباتي",
        ]

        is_trend_question = any(
            keyword in text for keyword in trend_keywords
        )

        if is_trend_question:
            region_id = None
            start_year = None
            end_year = None
            include_forecasts = any(
                word in text
                for word in [
                    "forecast",
                    "prediction",
                    "predict",
                    "توقع",
                ]
            )

            # Extract a region ID, e.g. "region 1" or "المنطقة 1".
            region_match = re.search(
                r"(?:region|المنطقة)\s*#?\s*(\d+)",
                text,
                re.IGNORECASE,
            )

            if region_match:
                region_id = int(region_match.group(1))

            # Extract years such as 2020 or 1995.
            years = re.findall(
                r"\b(?:19|20)\d{2}\b",
                text,
            )

            if len(years) >= 2:
                start_year = int(years[0])
                end_year = int(years[1])
            elif len(years) == 1:
                start_year = int(years[0])
                end_year = int(years[0])

            # Call the MCP tool, not TrendAgent directly.
            mcp_result = run_mcp_tool(
                "analyze_vegetation_trends",
                {
                    "region_id": region_id or 0,
                    "start_year": start_year or 0,
                    "end_year": end_year or 0,
                    "include_forecasts": include_forecasts,
                },
            )

            return {
                "success": not mcp_result["is_error"],
                "question": question,
                "supervisor": "Supervisor",
                "agent": "TrendAgent",
                "mcp_tool": mcp_result["tool"],
                "result": mcp_result["content"],
            }

        # 2. Route toxic plants.
        if any(
            word in text
            for word in [
                "toxic",
                "poison",
                "poisonous",
                "سامة",
                "سام",
                "سمية",
            ]
        ):
            data_type = "toxic"
            agent = "PlantAgent"

        # 3. Route rare plants.
        elif any(
            word in text
            for word in [
                "rare",
                "rarity",
                "نادر",
                "نادرة",
                "نادره",
            ]
        ):
            data_type = "rare"
            agent = "PlantAgent"

        # 4. Route beneficial plants.
        elif any(
            word in text
            for word in [
                "benefit",
                "benefits",
                "useful",
                "medicinal",
                "فوائد",
                "نافعة",
                "نافعه",
                "مفيدة",
                "مفيده",
            ]
        ):
            data_type = "benefits"
            agent = "PlantAgent"

        # 5. Route other plant distribution queries.
        else:
            data_type = "distribution"
            agent = "VegetationAgent"

        mcp_result = run_mcp_tool(
            "search_plant_data",
            {
                "query": "",
                "data_type": data_type,
            },
        )

        return {
            "success": not mcp_result["is_error"],
            "question": question,
            "supervisor": "Supervisor",
            "agent": agent,
            "mcp_tool": mcp_result["tool"],
            "data_type": data_type,
            "result": mcp_result["content"],
        }
