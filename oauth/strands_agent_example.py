"""Interactive Strands agent using OAuth-authenticated MCP tools and local audio upload."""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import httpx2
from fastmcp import Client
from fastmcp.client.auth import OAuth
from mcp.client.streamable_http import streamable_http_client
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient


MCP_URL = "https://mcp.visualdimension.ai/mcp"
CLIENT_ID = "7ish6536fl8hj8ngjda1aps8hj"


MODEL_ID = "us.anthropic.claude-sonnet-4-6"


@tool
def upload_audio(file_path: str, upload_url: str) -> dict:
    """Upload a local audio file to S3 using a presigned PUT URL.

    Args:
        file_path: Local audio file path.
        upload_url: Full S3 presigned PUT URL.
    """
    path = Path(file_path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    with httpx2.Client(timeout=300, follow_redirects=False) as client:
        with path.open("rb") as file:
            response = client.put(upload_url, content=file)
            response.raise_for_status()

    return {
        "uploaded": True,
        "filename": path.name,
        "uploaded_bytes": path.stat().st_size,
        "http_status": response.status_code,
    }


async def authenticate():
    oauth = OAuth(
        mcp_url=MCP_URL,
        client_id=CLIENT_ID,
        callback_host="127.0.0.1",
        callback_port=8765,
        scopes=["openid"],
    )

    async with Client(MCP_URL, auth=oauth):
        tokens = await oauth.token_storage_adapter.get_tokens()
        if tokens is None or not tokens.access_token:
            raise RuntimeError("OAuth login did not produce an access token")

        return tokens.access_token


def create_streamable_http_transport(access_token):
    @asynccontextmanager
    async def transport():
        async with httpx2.AsyncClient(
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=httpx2.Timeout(30, read=300),
        ) as http_client:
            async with streamable_http_client(
                MCP_URL,
                http_client=http_client,
            ) as streams:
                yield streams

    return transport


def run_agent():
    access_token = asyncio.run(authenticate())

    bedrock_model = BedrockModel(
        model_id=MODEL_ID,
        region_name="us-east-1",
        streaming=True,
    )

    mcp_client = MCPClient(create_streamable_http_transport(access_token))

    with mcp_client:
        oauth_tools = mcp_client.list_tools_sync()
        all_tools = [*oauth_tools, upload_audio]
        print('Tools:', [tool.tool_name for tool in all_tools])

        agent = Agent(
            model=bedrock_model,
            tools=all_tools,
            system_prompt=(
                "Use the available OAuth MCP tools when appropriate. "
                "When requested to create video from audio use MCP registration tool first "
                "to obtain the presigned upload_url, then call the local upload_audio tool."
            ),
        )

        print("OAuth MCP agent ready. Type 'exit' to quit.")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in {"exit", "quit", "bye"}:
                break

            if user_input:
                agent(user_input)
                print("\n")


if __name__ == "__main__":
    run_agent()
