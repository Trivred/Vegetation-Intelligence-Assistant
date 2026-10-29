from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from asgiref.sync import async_to_sync

from chatbot.data_service import search_plants
from chatbot.agents import (
    PlantAgent,
    VegetationAgent,
    TrendAgent,
)
from chatbot.supervisor import Supervisor
from chatbot.mcp_client import (
    list_mcp_tools,
    list_mcp_resources,
    get_mcp_resource,
    get_mcp_prompt,
)


def format_natural_response(result):
    """
    Convert agent results into readable Arabic text.
    Supports strings, dictionaries, lists, and common data structures.
    """

    if result is None:
        return "ما حصلت على بيانات لعرضها."

    if isinstance(result, str):
        return result.strip() or "ما حصلت على بيانات لعرضها."

    if isinstance(result, list):
        if not result:
            return "ما حصلت على نتائج مطابقة لطلبك."

        items = []

        for index, item in enumerate(result, start=1):
            if isinstance(item, dict):
                item_text = format_natural_response(item)
                items.append(f"{index}. {item_text}")
            else:
                items.append(f"{index}. {str(item)}")

        return "\n".join(items)

    if isinstance(result, dict):
        # Prefer an existing natural-language answer if provided by an agent.
        for key in (
            "answer",
            "response",
            "message",
            "natural_response",
            "summary",
            "description",
        ):
            value = result.get(key)

            if isinstance(value, str) and value.strip():
                return value.strip()

        # Otherwise, format the available fields as readable text.
        lines = []

        friendly_names = {
            "success": "حالة العملية",
            "plant_name": "اسم النبات",
            "scientific_name": "الاسم العلمي",
            "region": "المنطقة",
            "regions": "المناطق",
            "type": "النوع",
            "benefits": "الفوائد",
            "toxicity": "السُمية",
            "rarity": "الندرة",
            "distribution": "الانتشار",
            "count": "العدد",
            "total": "الإجمالي",
            "year": "السنة",
            "trend": "الاتجاه",
            "data": "البيانات",
            "results": "النتائج",
            "error": "الخطأ",
        }

        ignored_keys = {
            "success",
            "status",
            "agent",
            "agent_name",
            "metadata",
            "debug",
        }

        for key, value in result.items():
            if key in ignored_keys or value is None:
                continue

            label = friendly_names.get(
                key,
                key.replace("_", " ").strip().capitalize(),
            )

            if isinstance(value, (dict, list)):
                formatted_value = format_natural_response(value)
            elif isinstance(value, bool):
                formatted_value = "نعم" if value else "لا"
            else:
                formatted_value = str(value)

            if formatted_value.strip():
                lines.append(f"{label}: {formatted_value}")

        if lines:
            return "\n".join(lines)

        return "تمت معالجة طلبك، لكن ما فيه تفاصيل متاحة لعرضها."

    return str(result)


class AssistantStatusAPIView(APIView):
    def get(self, request):
        return Response({
            "project": "Vegetation Intelligence Assistant",
            "status": "running",
            "data_source": "Excel files",
            "agents": [
                "PlantAgent",
                "VegetationAgent",
                "TrendAgent",
            ],
        })


class PlantSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        data_type = request.query_params.get(
            "type", "distribution"
        ).strip().lower()

        try:
            result = search_plants(
                query=query,
                data_type=data_type,
            )

            return Response(result)

        except Exception:
            return Response(
                {
                    "success": False,
                    "error": "تعذر البحث في بيانات النباتات حاليًا.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PlantAgentAPIView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        data_type = request.query_params.get(
            "type", "benefits"
        ).strip().lower()

        try:
            result = PlantAgent().run(
                query=query,
                data_type=data_type,
            )

            return Response(result)

        except Exception:
            return Response(
                {
                    "success": False,
                    "error": "تعذر الحصول على بيانات النباتات حاليًا.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VegetationAgentAPIView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "").strip()

        try:
            result = VegetationAgent().run(query=query)
            return Response(result)

        except Exception:
            return Response(
                {
                    "success": False,
                    "error": "تعذر تحليل بيانات الغطاء النباتي حاليًا.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TrendAgentAPIView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "").strip()

        try:
            result = TrendAgent().run(query=query)
            return Response(result)

        except Exception:
            return Response(
                {
                    "success": False,
                    "error": "تعذر تحليل اتجاهات الغطاء النباتي حاليًا.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    # الأسئلة المسموح للمستخدم باختيارها.
    ALLOWED_QUESTIONS = {
        "rare_all": {
            "data_type": "rare",
            "answer_type": "plant_list",
            "title": "النباتات النادرة",
        },
        "rare_region": {
            "data_type": "rare",
            "answer_type": "plant_list",
            "title": "النباتات النادرة حسب المنطقة",
        },
        "rare_level": {
            "data_type": "rare",
            "answer_type": "plant_list",
            "title": "مستويات الندرة",
        },
        "toxic_all": {
            "data_type": "toxic",
            "answer_type": "plant_list",
            "title": "النباتات السامة",
        },
        "toxic_region": {
            "data_type": "toxic",
            "answer_type": "plant_list",
            "title": "النباتات السامة حسب المنطقة",
        },
        "benefits_all": {
            "data_type": "benefits",
            "answer_type": "plant_list",
            "title": "النباتات النافعة",
        },
        "benefits_uses": {
            "data_type": "benefits",
            "answer_type": "plant_list",
            "title": "فوائد النباتات",
        },
        "dist_region": {
            "data_type": "distribution",
            "answer_type": "plant_list",
            "title": "توزيع النباتات حسب المنطقة",
        },
        "dist_plant": {
            "data_type": "distribution",
            "answer_type": "plant_list",
            "title": "مناطق انتشار نبات",
        },
        "trend_year": {
            "data_type": "trends",
            "answer_type": "trend",
            "title": "تغير الغطاء النباتي خلال السنوات",
        },
        "trend_region": {
            "data_type": "trends",
            "answer_type": "trend",
            "title": "مؤشر NDVI حسب المنطقة",
        },
        "trend_forecast": {
            "data_type": "trends",
            "answer_type": "trend",
            "title": "توقعات الغطاء النباتي",
        },
    }

    def post(self, request):
        question_id = request.data.get("question_id")

        if not isinstance(question_id, str):
            return Response(
                {
                    "success": False,
                    "error": "اختاري سؤالًا من القائمة.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        question_config = self.ALLOWED_QUESTIONS.get(question_id)

        if not question_config:
            return Response(
                {
                    "success": False,
                    "error": "هذا السؤال غير متاح. اختاري سؤالًا من القائمة.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data_type = question_config["data_type"]

        try:
            # أسئلة النباتات تُجاب مباشرة من ملف Excel.
            if data_type != "trends":
                query = request.data.get("query", "")
                region = request.data.get("region", "")

                if not isinstance(query, str) or not isinstance(region, str):
                    return Response(
                        {
                            "success": False,
                            "error": "تحققي من قيمة البحث أو المنطقة.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                query = query.strip()
                region = region.strip()

                if question_id in {
                    "rare_region",
                    "toxic_region",
                    "dist_region",
                } and not region:
                    return Response(
                        {
                            "success": False,
                            "error": "اختاري المنطقة أولًا.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if question_id == "dist_plant" and not query:
                    return Response(
                        {
                            "success": False,
                            "error": "اكتبي اسم النبات أو اختاريه.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # لا نبحث في جميع المناطق إذا اختار المستخدم منطقة محددة.
                search_query = region if region else query

                result = search_plants(
                    query=search_query,
                    data_type=data_type,
                    limit=100,
                )

                rows = result.get("results", [])

                # التأكد من وجود نتائج مطابقة.
                if not rows:
                    return Response({
                        "success": True,
                        "question": question_config["title"],
                        "answer": "ما لقيت سجلات مطابقة في ملف البيانات المحدد.",
                        "total_results": 0,
                        "results": [],
                    })

                return Response({
                    "success": True,
                    "question": question_config["title"],
                    "answer": (
                        f"وجدت {result['total_results']} سجلًا مطابقًا "
                        "في ملف البيانات."
                    ),
                    "total_results": result["total_results"],
                    "results": rows,
                    "columns": result.get("columns", []),
                })

            # أسئلة الاتجاهات لا تُحوّل إلى بحث نباتات.
            # نحتاج معالجتها عبر TrendAgent بعد التأكد من واجهته.
            return Response(
                {
                    "success": False,
                    "error": (
                        "تحليل الاتجاهات قيد الربط. "
                        "اختاري سؤالًا عن النباتات حاليًا."
                    ),
                },
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        except Exception:
            import traceback
            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "error": "تعذر قراءة البيانات. تحققي من ملفات Excel.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class MCPToolsAPIView(APIView):
    def get(self, request):
        try:
            tools = async_to_sync(list_mcp_tools)()

            return Response({
                "success": True,
                "tools": tools,
            })

        except Exception as error:
            return Response(
                {
                    "success": False,
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MCPResourcesAPIView(APIView):
    def get(self, request):
        try:
            resources = async_to_sync(list_mcp_resources)()

            return Response({
                "success": True,
                "resources": resources,
            })

        except Exception as error:
            return Response(
                {
                    "success": False,
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MCPResourceReadAPIView(APIView):
    def get(self, request):
        resource_uri = request.query_params.get(
            "uri", "vegetation://datasets"
        )

        try:
            content = async_to_sync(get_mcp_resource)(resource_uri)

            return Response({
                "success": True,
                "uri": resource_uri,
                "content": content,
            })

        except Exception as error:
            return Response(
                {
                    "success": False,
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MCPPromptAPIView(APIView):
    def get(self, request):
        question = request.query_params.get(
            "question", ""
        ).strip()

        if not question:
            return Response(
                {
                    "error": "يرجى إدخال السؤال في معامل question."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            messages = async_to_sync(get_mcp_prompt)(
                "vegetation_research_prompt",
                {"question": question},
            )

            return Response({
                "success": True,
                "prompt": "vegetation_research_prompt",
                "messages": messages,
            })

        except Exception as error:
            return Response(
                {
                    "success": False,
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AssistantPageView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return render(request, "assistant.html")
