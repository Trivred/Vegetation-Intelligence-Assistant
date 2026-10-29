from chatbot.supervisor import Supervisor

supervisor = Supervisor()

questions = [
    "Analyze historical vegetation trends",
    "Analyze vegetation in region 1",
    "What is the NDVI in 2020?",
    "ما توقعات الغطاء النباتي؟",
]

for question in questions:
    print("\nQUESTION:", question)
    result = supervisor.route(question)

    print("SUCCESS:", result["success"])
    print("AGENT:", result["agent"])

    if result["agent"] == "TrendAgent":
        trend = result["result"]

        print("STATUS:", trend["status"])
        print("REGION:", trend.get("region_id"))
        print("SELECTED YEAR:", trend.get("selected_year"))

    else:
        print("DATA TYPE:", result.get("data_type"))
