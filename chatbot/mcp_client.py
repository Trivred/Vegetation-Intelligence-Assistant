import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def fix_encoding(value):
    """Fix incorrectly decoded UTF-8 text recursively."""
    if isinstance(value, dict):
        return {
            key: fix_encoding(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [fix_encoding(item) for item in value]

    if isinstance(value, str) and ("Ø" in value or "Ù" in value):
        try:
            return value.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return value

    return value

async def call_mcp_tool(tool_name: str, arguments: dict | None = None):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "chatbot.mcp_server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments or {},
            )

            output = []

            for item in result.content:
                if hasattr(item, "text"):
                    try:
                        output.append(fix_encoding(json.loads(item.text)))
                    except (json.JSONDecodeError, TypeError):
                        output.append(fix_encoding(item.text))

            return {
                "tool": tool_name,
                "is_error": result.isError,
                "content": output,
            }


def run_mcp_tool(tool_name: str, arguments: dict | None = None):
    return asyncio.run(call_mcp_tool(tool_name, arguments))

async def list_mcp_tools():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "chatbot.mcp_server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()

            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                }
                for tool in result.tools
            ]


async def list_mcp_resources():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "chatbot.mcp_server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_resources()

            return [
                {
                    "uri": str(resource.uri),
                    "name": resource.name,
                }
                for resource in result.resources
            ]


async def get_mcp_resource(resource_uri: str):
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "chatbot.mcp_server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.read_resource(resource_uri)

            return [
                getattr(item, "text", str(item))
                for item in result.contents
            ]


async def get_mcp_prompt(prompt_name: str, arguments: dict):
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "chatbot.mcp_server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.get_prompt(
                prompt_name,
                arguments=arguments,
            )

            return [
                getattr(message.content, "text", str(message.content))
                for message in result.messages
            ]
