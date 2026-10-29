import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))

    params = StdioServerParameters(
        command=sys.executable,
        args=["-u", "-m", "chatbot.mcp_server"],
        cwd=project_dir,
        env={
            **os.environ,
            "PYTHONUNBUFFERED": "1",
        },
    )

    print("Project directory:", project_dir)
    print("Python executable:", sys.executable)
    print("Starting MCP server...")

    try:
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("MCP connection established!")

                result = await session.list_tools()

                for tool in result.tools:
                    print(f"- {tool.name}: {tool.description}")

    except Exception as error:
        print("\nConnection failed:")
        print(repr(error))

        if isinstance(error, BaseExceptionGroup):
            for group in error.exceptions:
                print("\nNested error:", repr(group))
                if isinstance(group, BaseExceptionGroup):
                    for nested in group.exceptions:
                        print("Root error:", repr(nested))


if __name__ == "__main__":
    asyncio.run(main())
