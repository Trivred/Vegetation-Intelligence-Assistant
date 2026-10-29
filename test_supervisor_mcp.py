from pprint import pprint

from chatbot.supervisor import Supervisor

supervisor = Supervisor()

questions = [
   
    "ما توقعات الغطاء النباتي؟",
    "ما النباتات النادرة؟",
    "ما النباتات السامة؟",
    "ما النباتات النافعة؟",
]

for question in questions:
    print("\n" + "=" * 70)
    print("QUESTION:", question)

    try:
        result = supervisor.route(question)
        pprint(result)
    except Exception as error:
        print("ERROR:", repr(error))
