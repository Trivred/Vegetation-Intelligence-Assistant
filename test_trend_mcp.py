from chatbot.mcp_server import analyze_vegetation_trends

print("=== ALL HISTORICAL DATA ===")
print(analyze_vegetation_trends())

print("\n=== REGION 1 ===")
print(analyze_vegetation_trends(region_id=1))

print("\n=== YEAR 2020 ===")
print(
    analyze_vegetation_trends(
        start_year=2020,
        end_year=2020,
    )
)

print("\n=== FORECASTS ===")
print(
    analyze_vegetation_trends(
        start_year=2027,
        end_year=2029,
        include_forecasts=True,
    )
)
