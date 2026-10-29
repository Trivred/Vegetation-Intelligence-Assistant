from django.urls import path

from chatbot.views import (
    AssistantStatusAPIView,
    AssistantPageView,
    PlantSearchAPIView,
    PlantAgentAPIView,
    VegetationAgentAPIView,
    TrendAgentAPIView,
    ChatAPIView,
    MCPToolsAPIView,
    MCPResourcesAPIView,
    MCPResourceReadAPIView,
    MCPPromptAPIView,
)

urlpatterns = [
    path("", AssistantPageView.as_view(), name="assistant_page"),
    path("status/", AssistantStatusAPIView.as_view(), name="assistant_status"),
    path("plants/", PlantSearchAPIView.as_view(), name="plant_search"),
    path("agents/plants/", PlantAgentAPIView.as_view(), name="plant_agent"),
    path("agents/vegetation/", VegetationAgentAPIView.as_view(), name="vegetation_agent"),
    path("agents/trends/", TrendAgentAPIView.as_view(), name="trend_agent"),
    path("chat/", ChatAPIView.as_view(), name="chat"),
    path("mcp/tools/", MCPToolsAPIView.as_view(), name="mcp_tools"),
    path("mcp/resources/", MCPResourcesAPIView.as_view(), name="mcp_resources"),
    path("mcp/resource/", MCPResourceReadAPIView.as_view(), name="mcp_resource_read"),
    path("mcp/prompt/", MCPPromptAPIView.as_view(), name="mcp_prompt"),
]
