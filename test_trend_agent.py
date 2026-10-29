from chatbot.agents import TrendAgent

agent = TrendAgent()

# Test the overall historical trend.
result = agent.run(query="Analyze historical vegetation trends")

print("OVERALL TREND")
print(result)

# Test a specific region.
region_result = agent.run(
    query="Analyze vegetation in region 1",
    region_id=1,
)

print("\nREGION 1")
print(region_result)

# Test a specific year.
year_result = agent.run(
    query="Analyze vegetation in 2020",
    year=2020,
)

print("\nYEAR 2020")
print(year_result)
