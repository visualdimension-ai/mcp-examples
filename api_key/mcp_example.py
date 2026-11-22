"""Interactive MCP client test."""

import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


MCP_URL = "https://mcp.visualdimension.ai/mcp-apikey"
USER_ID = "YOUR-USER-ID"
API_KEY = "YOUR-API-KEY"


async def main():
    transport = StreamableHttpTransport(
        url=MCP_URL,
        headers={
            "x-api-key": API_KEY,
            "x-user-id": USER_ID,
        },
    )

    async with Client(transport) as client:
        tools = await client.list_tools()
        for tool in tools:
            print("Tool:", tool.name)

        result = await client.call_tool(
            "vd___search_videos",
            {},
        )
        print("Search results:", result)


if __name__ == "__main__":
    asyncio.run(main())
