"""Interactive Strands agent using API-key-authenticated MCP tools and local audio upload."""

from contextlib import asynccontextmanager

import httpx2
from mcp.client.streamable_http import streamable_http_client
from pathlib import Path

from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient


MCP_URL = "https://mcp.visualdimension.ai/mcp-apikey"
USER_ID = "YOUR-USER-ID"
API_KEY = "YOUR-API-KEY"

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


@asynccontextmanager
async def create_streamable_http_transport():
    """Create authenticated MCP transport."""

    headers = {
        "x-api-key": API_KEY,
        "x-user-id": USER_ID,
    }

    async with httpx2.AsyncClient(
        headers=headers,
        timeout=httpx2.Timeout(30, read=300),
    ) as http_client:
        async with streamable_http_client(
            MCP_URL,
            http_client=http_client,
        ) as (read, write):
            yield read, write


def run_agent():
    bedrock_model = BedrockModel(
        model_id=MODEL_ID,
        region_name="us-east-1",
        streaming=True,
    )

    mcp_client = MCPClient(create_streamable_http_transport)

    with mcp_client:
        mcp_tools = mcp_client.list_tools_sync()
        all_tools = [*mcp_tools, upload_audio]
        print("Tools:", [tool.tool_name for tool in all_tools])

        agent = Agent(
            model=bedrock_model,
            tools=all_tools,
            system_prompt=(
                "Use the available API-key-authenticated MCP tools when appropriate. "
                "When requested to create video from audio use MCP registration tool first "
                "to obtain the presigned upload_url, then call the local upload_audio tool."
            ),
        )

        print("API-key MCP agent ready. Type 'exit' to quit.")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in {"exit", "quit", "bye"}:
                break

            if user_input:
                agent(user_input)
                print("\n")


if __name__ == "__main__":
    run_agent()
