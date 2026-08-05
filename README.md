# Observability for AI Agents: Making the Invisible Visible

[![License](https://img.shields.io/badge/License-MIT--0-blue.svg?style=for-the-badge)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python)](https://python.org) [![Strands](https://img.shields.io/badge/Strands_Agents-1.47.0-blue.svg?style=for-the-badge)](https://strandsagents.com/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) [![Amazon Bedrock AgentCore](https://img.shields.io/badge/Amazon_Bedrock-AgentCore-FF9900.svg?style=for-the-badge)](https://aws.amazon.com/bedrock/agentcore/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)

**An AI agent's reasoning steps, tool-call cascades, and per-cycle token cost are invisible by default — until you instrument them.** This repo is four progressive demos, each keyed to a specific section of the [Strands Agents observability documentation](https://strandsagents.com/docs/user-guide/observability-evaluation/observability/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el), that make a travel-booking agent's *normal* behavior visible: no injected failures, no chaos effects — just a real agent doing its job, seen through increasingly capable lenses.

> Strands is model-agnostic: its providers are interchangeable, so the same code runs on Amazon Bedrock, Anthropic, OpenAI, or a local model via Ollama. These demos default to **OpenAI `gpt-4o-mini`** because it needs only an API key to try. The same observability patterns carry over to other agent frameworks.

This sample works with [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) and [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el). Code in this repository is provided "as is", and is not officially supported by Amazon.

---

## Projects

| Project | Description | Stack |
|---------|-------------|-------|
| [**01 - Agent Metrics**](./01-agent-metrics/) | **Start here.** Runs a travel agent (search flights, check weather, book) and compares two lenses on the same run: traditional `logging.getLogger("strands")` vs. the SDK's built-in `result.metrics.get_summary()` — zero extra install, zero extra config. | ![Metrics](https://img.shields.io/badge/-Metrics-blue) ![Strands](https://img.shields.io/badge/-Strands_Agents-orange) |
| [**02 - OpenTelemetry Traces**](./02-opentelemetry-traces/) | Turns on `StrandsTelemetry` to see the full **Agent → Cycle → Model → Tool** span hierarchy for the same agent — the documented OpenTelemetry integration, printed to console or exported to a local Jaeger collector. | ![Traces](https://img.shields.io/badge/-OpenTelemetry-blueviolet) ![Strands](https://img.shields.io/badge/-Strands_Agents-orange) |
| [**03 - Custom Trace Attributes**](./03-custom-trace-attributes/) | Tags a span with a **business** fact (e.g. "was this a high-value booking?"), not just a technical one — combining agent-level `trace_attributes` with an `AfterToolCallEvent` hook and a custom span. | ![Hooks](https://img.shields.io/badge/-Hooks-green) ![Strands](https://img.shields.io/badge/-Strands_Agents-orange) |
| [**04 - AgentCore Observability**](./04-agentcore-observability/) | Deploys the same agent to **Amazon Bedrock AgentCore Runtime**, where traces no longer live in your terminal — they live in **Amazon CloudWatch GenAI Observability**, with automatic OpenTelemetry instrumentation. | ![AgentCore](https://img.shields.io/badge/-AgentCore-FF9900) ![CloudWatch](https://img.shields.io/badge/-CloudWatch-FF9900) |

---

## The Big Picture

Every demo instruments the **same travel agent** (real Duffel sandbox flight search, real Open-Meteo weather, a local SQLite booking ledger) doing its normal job. Nothing is broken on purpose. The only thing that changes, demo to demo, is how much of the agent's internal behavior becomes visible, and where that visibility lives:

```
01 Agent Metrics          → your terminal, zero config     (result.metrics.get_summary())
02 OpenTelemetry Traces   → your terminal or a local Jaeger (StrandsTelemetry)
03 Custom Trace Attributes → the same traces, business-tagged (trace_attributes + hooks)
04 AgentCore Observability → Amazon CloudWatch, in production (AgentCore Runtime)
```

> This repo is about **observability** — seeing what an agent already does. It is deliberately *not* about resilience or chaos testing (injecting failures and recovering from them); that is a different story, told elsewhere.

---

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- An `OPENAI_API_KEY` (default), **or** AWS credentials with Amazon Bedrock access
- A free [Duffel sandbox](https://app.duffel.com) token (More → Developers → Access tokens)
- Demo 04 additionally needs AWS credentials with Amazon Bedrock AgentCore access

---

## Quick Start

```bash
git clone https://github.com/elizabethfuentes12/observability-for-agents-sample-for-aws.git
cd observability-for-agents-sample-for-aws/01-agent-metrics

uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env   # then fill in OPENAI_API_KEY and DUFFEL_API_KEY
uv run python test_agent_metrics.py
```

Each demo folder is self-contained with its own `requirements.txt`, `.env.example`, and Python script. Demos 01-03 also include a Jupyter notebook with the same story, step by step.

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| [**Strands Agents**](https://strandsagents.com/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) | The agent harness: agent loop, tools, hooks, native metrics and OpenTelemetry tracing |
| [**OpenAI**](https://platform.openai.com/) | Default model `gpt-4o-mini`, so the demos need only an API key to try |
| [**Amazon Bedrock**](https://aws.amazon.com/bedrock/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) | The Strands default provider; switch by editing the model block in each demo |
| [**Amazon Bedrock AgentCore**](https://aws.amazon.com/bedrock/agentcore/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) | Production runtime with automatic OpenTelemetry instrumentation (demo 04) |
| [**Duffel**](https://duffel.com) | Real sandbox flight fares the travel agent searches and books against |
| [**OpenTelemetry**](https://opentelemetry.io/) | The tracing standard Strands' native instrumentation is built on |

---

## Frequently asked questions

**What's the difference between this repo and a resilience/chaos-testing demo?**
This repo is about **visibility**: making an agent's normal reasoning, tool calls, and cost visible. It never injects a failure. A resilience demo (chaos testing, fallback hooks, recovery) is a different, related story — not what's covered here.

**Do I need OpenTelemetry for every demo?**
No. Demo 01 uses only `result.metrics.get_summary()` — already part of `strands-agents`, no `[otel]` extra. Demos 02-04 build on OpenTelemetry tracing.

**Does this only work with Strands Agents or AWS?**
No. An agent loop, hooks, metrics, and OpenTelemetry tracing are general agent-observability concepts. The demos use [Strands Agents](https://strandsagents.com/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) because these primitives are built in, and Strands is model-agnostic, so they run on OpenAI by default or on Amazon Bedrock, Anthropic, or a local Ollama model with no change to the agent code.

---

## Contributing

Contributions are welcome! See [CONTRIBUTING](CONTRIBUTING.md) for more information.

---

## Security

If you discover a potential security issue in this project, notify AWS/Amazon Security via the [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public GitHub issue.

---

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file for details.
