# MCP examples

Examples for connecting to VisualDimension MCP servers using either API-key or
OAuth authentication. The repository includes direct MCP clients and Strands
agents that can use the available MCP tools.

The examples were tested with **Python 3.11**.

## Requirements

- Python 3.11
- Network access to the VisualDimension MCP server
- Credentials appropriate for the example you want to run
- AWS credentials with Amazon Bedrock access for the Strands agent examples

The pinned Python dependencies are listed in [`requirements.txt`](requirements.txt).
The `mcp` package is installed transitively by `fastmcp`.

## Installation

Create and activate a virtual environment, then install the dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Examples

### API-key MCP client

[`api_key/mcp_client_example.py`](api_key/mcp_client_example.py) connects to
the API-key-authenticated MCP endpoint, lists the available tools, and calls
the video search tool.

Before running it, replace `YOUR-USER-ID` and `YOUR-API-KEY` in the file with
your VisualDimension credentials:

```bash
python api_key/mcp_client_example.py
```

### API-key Strands agent

[`api_key/strands_agent_example.py`](api_key/strands_agent_example.py) creates
an interactive Strands agent backed by Amazon Bedrock and API-key-authenticated
MCP tools. It also includes a local tool for uploading audio through a
presigned URL.

Replace `YOUR-USER-ID` and `YOUR-API-KEY` before starting the agent. Configure
AWS credentials and permissions for the Bedrock model specified by `MODEL_ID`.

```bash
python api_key/strands_agent_example.py
```

Type `exit`, `quit`, or `bye` to stop the agent.

### OAuth MCP client

[`oauth/mcp_client_example.py`](oauth/mcp_client_example.py) authenticates with
OAuth, lists the available tools, and calls the video search tool. Running it
opens the OAuth login flow in a browser and uses the local callback address
`127.0.0.1:8765`.

```bash
python oauth/mcp_client_example.py
```

### OAuth Strands agent

[`oauth/strands_agent_example.py`](oauth/strands_agent_example.py) creates an
interactive Strands agent backed by Amazon Bedrock and OAuth-authenticated MCP
tools. It also supports uploading a local audio file through a presigned URL.

The OAuth example uses the client ID included in the file and requires browser
access to complete authentication. Configure AWS credentials and permissions
for the Bedrock model specified by `MODEL_ID`.

```bash
python oauth/strands_agent_example.py
```

Type `exit`, `quit`, or `bye` to stop the agent.
