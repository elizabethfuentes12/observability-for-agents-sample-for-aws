# boto3 deploy — Travel Agent on Amazon Bedrock AgentCore

Step-by-step deployment using boto3 directly, so you can see every AWS API call being made. Good for learning the internals, workshops, or debugging.

## Prerequisites

- AWS credentials configured (`aws configure`)
- Python 3.11+, [`uv`](https://docs.astral.sh/uv/) — no local Docker needed; the container image is built remotely by AWS CodeBuild
- CloudWatch Transaction Search enabled once per account — see [official guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#observability-configure-builtin)
- Bedrock model access to `us.anthropic.claude-sonnet-4-5` (or override)
- A free [Duffel sandbox token](https://app.duffel.com)

## Deploy

```bash
cd 04-agentcore-observability/boto3

# 1. Install deps
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Configure env (create .env from .env.example)
cp .env.example .env
# then edit .env and set DUFFEL_API_KEY, AWS_REGION

# 3. Run the deployer
uv run python deploy_agentcore.py
```

The script prints each step as it goes:

```
Step 1: DynamoDB table
  ✓ Created FlightBookings
Step 2: IAM roles
  ✓ Created travel-agent-lambda-execution-role
  ✓ Created travel-agent-agentcore-execution-role
Step 3: Tool Lambdas
  ✓ Created travel-agent-search_flights
  ✓ Created travel-agent-get_weather
  ✓ Created travel-agent-book_flight
Step 4: AgentCore Gateway
  ✓ Created TravelAgentGateway
Step 5: Gateway targets
  ✓ Created target search-flights
  ✓ Created target get-weather
  ✓ Created target book-flight
Step 6: AgentCore Runtime (via bedrock-agentcore-starter-toolkit)
  ✓ Runtime ready: arn:aws:bedrock-agentcore:us-east-1:...:runtime/TravelAgentRuntime-abc123
Step 7: Smoke-test invocation
  agent responded: ...
```

Total time: ~10–12 minutes (most of it is CodeBuild building the Docker image).

## Invoke your agent

```bash
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "<ARN from deploy output>" \
  --payload "$(echo '{"prompt": "Book a one-way JFK to MIA next Friday for John Doe. Will he need a jacket?"}' | base64)" \
  --region us-east-1 \
  /tmp/response.json

cat /tmp/response.json
```

## Cleanup

```bash
uv run python cleanup.py
```

Deletes runtime → gateway (with targets) → Lambdas → IAM roles → DynamoDB table → ECR repo + CodeBuild project the starter toolkit created → local `.bedrock_agentcore*.yaml` state files.

## Idempotency

`deploy_agentcore.py` is safe to re-run. Each step checks whether the resource already exists and reuses it. If a Lambda already exists, its code is updated in place. If the gateway or runtime already exists, they're left as-is.

## File structure

```
boto3/
├── deploy_agentcore.py           # Runs all deploy steps end-to-end
├── cleanup.py                    # Deletes everything deploy created
├── travel_agent.py               # AgentCore Runtime entrypoint
├── Dockerfile                    # Built by the starter toolkit
├── .dockerignore
├── agent_requirements.txt        # Runtime Python deps
├── requirements.txt              # Local deploy-script deps
├── .env.example
├── lambda_tools/
│   ├── search_flights/lambda_function.py
│   ├── get_weather/lambda_function.py
│   └── book_flight/lambda_function.py
└── tool_schemas/
    └── tools.json                # Same file as ../cdk/tool_schemas/tools.json
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
