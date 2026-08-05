# 04 — AgentCore Observability: The Travel Agent in Production

[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org) [![Strands Agents](https://img.shields.io/badge/Strands_Agents-1.47.0-blue.svg)](https://strandsagents.com/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) [![Amazon Bedrock AgentCore](https://img.shields.io/badge/Amazon_Bedrock-AgentCore-FF9900.svg)](https://aws.amazon.com/bedrock/agentcore/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) [![Amazon CloudWatch](https://img.shields.io/badge/CloudWatch-GenAI_Observability-FF9900.svg)](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/view-observability-data-cloudwatch.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)

> Demos 01-03 ran locally and printed metrics/traces to your terminal. Here we deploy **the same travel agent** to **Amazon Bedrock AgentCore Runtime** — the tools are now Lambda functions behind an **AgentCore Gateway**, and `book_flight` writes to **DynamoDB**. Everything the agent does becomes visible in **Amazon CloudWatch GenAI Observability** with automatic OpenTelemetry instrumentation.

---

## What's in this folder

Two ways to deploy the same thing. Pick one — you don't need both.

| Method | Folder | When to use it |
|---|---|---|
| **AWS CDK** | [`cdk/`](./cdk/) | Reproducible, single-command deployment (`cdk deploy`). Recommended if you already use CDK. |
| **boto3 script** | [`boto3/`](./boto3/) | Step-by-step deploy script that prints every AWS API call as it runs. Best for learning what's happening under the hood, or for workshops. |

Both deploy the **exact same infrastructure**: a Strands travel agent running on AgentCore Runtime, with three tools (`search_flights`, `get_weather`, `book_flight`) served via AgentCore Gateway as Lambda functions over MCP (Model Context Protocol), and a DynamoDB table for flight bookings.

---

## Architecture (what gets deployed)

```
                                                     ┌──────────────────────────────┐
                                                     │   AgentCore Runtime          │
    User invocation ─────────────────────────────►   │   ┌────────────────────┐    │
    (aws bedrock-agentcore invoke-agent-runtime)     │   │ travel_agent.py    │    │
                                                     │   │ (Strands + Bedrock │    │
                                                     │   │  Claude Sonnet)    │    │
                                                     │   └────────┬───────────┘    │
                                                     └────────────┼─────────────────┘
                                                                  │ MCP (streamable HTTP)
                                                                  ▼
                                                     ┌──────────────────────────────┐
                                                     │   AgentCore Gateway          │
                                                     │   (MCP endpoint, IAM auth)   │
                                                     └────────────┬─────────────────┘
                                                                  │
                              ┌───────────────────────────────────┼───────────────────────────────────┐
                              ▼                                   ▼                                   ▼
                    ┌──────────────────┐                ┌──────────────────┐                ┌──────────────────┐
                    │ Lambda:          │                │ Lambda:          │                │ Lambda:          │
                    │ search_flights   │                │ get_weather      │                │ book_flight      │
                    │ (Duffel API)     │                │ (Open-Meteo API) │                │ (DynamoDB write) │
                    └──────────────────┘                └──────────────────┘                └──────────┬───────┘
                                                                                                      │
                                                                                                      ▼
                                                                                            ┌──────────────────┐
                                                                                            │   DynamoDB       │
                                                                                            │   FlightBookings │
                                                                                            └──────────────────┘

     ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
     │  Everything above is auto-instrumented with OpenTelemetry by AgentCore Runtime.                  │
     │  Traces, metrics, and logs flow into Amazon CloudWatch GenAI Observability with zero extra code. │
     └──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## What you'll see in CloudWatch GenAI Observability

After deploying and invoking the agent, open the [CloudWatch GenAI Observability dashboard](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/view-observability-data-cloudwatch.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) and you'll find three views:

- **Agents View** — every AgentCore Runtime agent in your account, with runtime metrics (invocations, latency, errors).
- **Sessions View** — all sessions across your agents. Click one to see everything that happened during that request.
- **Traces View** — the full span tree from Demo 02 (`invoke_agent Strands Agents` → `execute_event_loop_cycle` → `chat` + `execute_tool <name>`), now living in CloudWatch instead of your terminal. Plus, the custom trace attributes from Demo 03 (`business.vip_booking`, session IDs) are searchable and filterable directly in the console.

---

## Prerequisites

Before deploying either version:

- **AWS account** with credentials configured (`aws configure`).
- **Model access** to `us.anthropic.claude-sonnet-4-5` (or your preferred Bedrock model) enabled in the [Bedrock console](https://console.aws.amazon.com/bedrock/home?#/modelaccess).
- **CloudWatch Transaction Search enabled** — first-time users of AgentCore Observability must enable this once per account. Follow the [official guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#observability-configure-builtin).
- **Python 3.11+** and [`uv`](https://docs.astral.sh/uv/) installed locally.
- A **Duffel sandbox token** for `search_flights` (free at [app.duffel.com](https://app.duffel.com) → More → Developers → Access tokens). Set it as `DUFFEL_API_KEY` in the environment the Lambda reads.

---

## Choosing between CDK and boto3

Both paths reach the same end state. Differences:

| | CDK | boto3 script |
|---|---|---|
| Deploy time | ~5–8 min | ~10–12 min (prints each step) |
| Command | `cdk deploy` | `uv run python deploy_agentcore.py` |
| Rollback | `cdk destroy` | `uv run python cleanup.py` |
| Best for | Reproducible deployment | Understanding each API call |
| Prerequisites | CDK v2 installed | boto3 + starter toolkit |

---

## After deploying — how to invoke your agent

Once deployed, both paths give you an **Agent Runtime ARN**. Invoke the agent from anywhere:

```bash
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "<ARN from deploy output>" \
  --payload "$(echo '{"prompt": "Book a one-way flight from JFK to MIA next Friday for John Doe and tell me if he needs a jacket."}' | base64)" \
  --region us-east-1 \
  /tmp/response.json

cat /tmp/response.json
```

Then open the CloudWatch GenAI Observability dashboard and find your session under **Sessions View**.

---

## Cleanup

Deleting the deployed resources completely:

- **CDK**: `cd cdk && cdk destroy`
- **boto3**: `cd boto3 && uv run python cleanup.py`

Both remove the AgentCore Runtime, Gateway, Lambda functions, IAM roles, ECR repo (if any), CodeBuild project (if any), and the DynamoDB `FlightBookings` table (`RemovalPolicy.DESTROY`).

---

## Frequently asked questions

**Do I need to deploy both the CDK and the boto3 versions?**
No. Both deploy the exact same infrastructure; pick the one that matches how you work. CDK for a reproducible one-command deploy, boto3 for seeing every API call.

**Why don't my traces appear in CloudWatch?**
The most common cause is CloudWatch Transaction Search not being enabled. It's a one-time, per-account setup — follow the [official guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#observability-configure-builtin) and invoke the agent again.

**Does cleanup really remove everything?**
Yes. Both paths delete the AgentCore Runtime, Gateway, Lambda functions, IAM roles, ECR repo and CodeBuild project (if created), and the DynamoDB `FlightBookings` table. No orphaned resources.

**Can I use a different Bedrock model?**
Yes. The default is `us.anthropic.claude-sonnet-4-5`; both paths let you override the model ID (CDK context / environment variable). Make sure the model is enabled in your account's Bedrock model access first.

---

## Note on this folder vs the video

This code is **not shown in the video** — the video walks through the *concepts* of AgentCore Observability using the CloudWatch console. The code here is what you use to reproduce the deployment on your own account. Everything is verified and runs against real AWS.

---

## References

- [Get started with AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-get-started.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)
- [View observability data in CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/view-observability-data-cloudwatch.html?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)
- [Amazon Bedrock AgentCore FAQs](https://aws.amazon.com/bedrock/agentcore/faqs/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)
- [Strands Agents on AgentCore Runtime](https://strandsagents.com/docs/user-guide/deploy/deploy_to_bedrock_agentcore/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)
- Previous demo in this repo: [03 - Custom Trace Attributes](../03-custom-trace-attributes/)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING](../CONTRIBUTING.md) for more information.

---

## Security

If you discover a potential security issue in this project, notify AWS/Amazon Security via the [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public GitHub issue.

---

## License

This library is licensed under the MIT-0 License. See the [LICENSE](../LICENSE) file for details.
