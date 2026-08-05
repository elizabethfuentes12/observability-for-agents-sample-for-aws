"""Travel agent runtime — deployed to Amazon Bedrock AgentCore Runtime.

Loads the AgentCore Gateway URL from an env var, connects via MCP streamable-HTTP, wraps
the agent with Strands, and exposes an /invocations endpoint through BedrockAgentCoreApp.

Observability is automatic when running inside AgentCore Runtime — no explicit
StrandsTelemetry setup is needed; the runtime instruments the process for you.
"""

import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

app = BedrockAgentCoreApp()

GATEWAY_URL = os.environ["AGENTCORE_GATEWAY_URL"]
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

SYSTEM_PROMPT = (
    "You are a travel assistant. Search flights, check the weather at the destination, "
    "and book the best option for the traveler without asking for confirmation. Be concise."
)

# Connect to the AgentCore Gateway once at cold start; the MCP client stays open across
# invocations. AgentCore Gateway signs requests with the runtime's IAM role, so no
# credentials are passed here.
_mcp = MCPClient(lambda: streamablehttp_client(GATEWAY_URL))
_mcp.__enter__()  # noqa: pylint keep-open
_tools = _mcp.list_tools_sync()

_model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)
_agent = Agent(model=_model, system_prompt=SYSTEM_PROMPT, tools=_tools)


@app.entrypoint
def invoke(payload: dict) -> str:
    """AgentCore Runtime entrypoint: JSON payload in, agent text response out."""
    prompt = payload.get("prompt", "")
    if not prompt:
        return "Please provide a 'prompt' field in the request payload."
    result = _agent(prompt)
    return result.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
