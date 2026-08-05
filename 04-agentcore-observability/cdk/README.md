# CDK deploy — Travel Agent on Amazon Bedrock AgentCore

Reproducible, one-command deployment of the whole system with AWS CDK.

## Prerequisites

- AWS credentials configured (`aws configure`)
- Python 3.11+, [`uv`](https://docs.astral.sh/uv/), Node.js 18+ (for the CDK CLI)
- CDK v2 installed globally: `npm install -g aws-cdk`
- CDK bootstrapped in your account/region: `cdk bootstrap`
- CloudWatch Transaction Search enabled once per account — see [official guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#observability-configure-builtin)
- A free [Duffel sandbox token](https://app.duffel.com) — set as `DUFFEL_API_KEY`
- Bedrock model access to `us.anthropic.claude-sonnet-4-5` (or override with a CDK context)

## Deploy

```bash
cd 04-agentcore-observability/cdk

# 1. Install CDK deps
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Build the agent deployment package (ARM64, Python 3.11)
./create_deployment_package.sh

# 3. Export the Duffel sandbox key
export DUFFEL_API_KEY=duffel_test_...

# 4. Deploy
cdk deploy TravelAgentObservabilityStack
```

Deploy takes ~5–8 minutes. The stack outputs:

- `AgentRuntimeArn` — invoke the agent with this ARN.
- `GatewayUrl` — the MCP endpoint the runtime talks to.
- `FlightBookingsTableName` — the DynamoDB table for confirmed bookings.

## Invoke

```bash
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "<AgentRuntimeArn from output>" \
  --payload "$(echo '{"prompt": "Book a one-way JFK to MIA next Friday for John Doe. Will he need a jacket?"}' | base64)" \
  --region us-east-1 \
  /tmp/response.json

cat /tmp/response.json
```

Then open **CloudWatch → GenAI Observability** in the AWS console to see traces, sessions, and metrics.

## Model override

The default is `us.anthropic.claude-sonnet-4-5`. Override at deploy time:

```bash
cdk deploy TravelAgentObservabilityStack -c bedrock_model_id=global.anthropic.claude-sonnet-4-6
```

## Cleanup

```bash
cdk destroy TravelAgentObservabilityStack
```

Everything (Runtime, Gateway, Lambdas, IAM role, DynamoDB table) is `RemovalPolicy.DESTROY`, so `cdk destroy` leaves the account clean.

## File structure

```
cdk/
├── app.py                        # CDK app entry
├── cdk.json
├── stack.py                      # TravelAgentObservabilityStack (one stack)
├── requirements.txt              # CDK deps
├── create_deployment_package.sh  # Builds agent_files/deployment_package.zip
├── agent_files/
│   ├── travel_agent.py           # AgentCore Runtime entrypoint
│   └── requirements.txt          # Runtime deps (strands-agents, mcp, ...)
├── lambda_tools/
│   ├── search_flights/lambda_function.py
│   ├── get_weather/lambda_function.py
│   └── book_flight/lambda_function.py
├── tool_schemas/
│   └── tools.json                # MCP tool schemas (shared source of truth)
└── agentcore/
    ├── __init__.py
    ├── agentcore_role.py         # IAM role construct
    ├── agentcore_gateway.py      # Gateway + Lambdas + targets construct
    └── agentcore_runtime.py      # Runtime construct
```

---

## Contributing

Contributions are welcome! See [CONTRIBUTING](../../CONTRIBUTING.md) for more information.

---

## Security

If you discover a potential security issue in this project, notify AWS/Amazon Security via the [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public GitHub issue.

---

## License

This library is licensed under the MIT-0 License. See the [LICENSE](../../LICENSE) file for details.
