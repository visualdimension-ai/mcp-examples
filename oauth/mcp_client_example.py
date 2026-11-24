"""Interactive MCP client test."""

import asyncio
from fastmcp import Client
from fastmcp.client.auth import OAuth


MCP_URL = "https://mcp.visualdimension.ai/mcp"
CLIENT_ID = "7ish6536fl8hj8ngjda1aps8hj"


async def main():
    oauth = OAuth(
        mcp_url=MCP_URL,
        client_id=CLIENT_ID,
        callback_host="127.0.0.1",
        callback_port=8765,
        scopes=["openid"],
    )
    async with Client(MCP_URL, auth=oauth) as client:
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
