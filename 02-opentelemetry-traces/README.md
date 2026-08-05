# OpenTelemetry Traces: Seeing the Full Agent → Cycle → LLM → Tool Tree

[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org) [![Strands Agents](https://img.shields.io/badge/Strands_Agents-1.47.0-blue.svg)](https://strandsagents.com/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) [![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-enabled-blueviolet.svg)](https://opentelemetry.io/) [![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991.svg?logo=openai)](https://platform.openai.com/)

> Demo 01 showed `result.metrics.get_summary()` — a flat snapshot for one run. This demo turns on **OpenTelemetry tracing**, so you see the actual hierarchical execution tree: which cycle called which model invocation, which invocation triggered which tool, in order, with timestamps.

> Uses **Strands Agents**' native OpenTelemetry integration. OTEL tracing is a general observability standard; the same patterns carry over to other agent frameworks.

---

## What does this demo show?

The [Strands traces guide](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) opens with:

> "Tracing is a fundamental component of the Strands SDK's observability framework... Using the OpenTelemetry standard, Strands traces capture the complete journey of a request through your agent, including LLM interactions, retrievers, tool usage, and event loop processing."

Turning it on is two lines:

```python
from strands.telemetry import StrandsTelemetry

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_console_exporter()   # print the trace tree to stdout
# strands_telemetry.setup_otlp_exporter()    # or send it to a real collector (Jaeger, CloudWatch, ...)
```

Every `Agent(...)` call made after this prints or exports a nested tree, exactly as documented in the [Trace Structure](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#4-trace-structure) section:

```
Strands Agent (gen_ai.usage.total_tokens, gen_ai.user.message, gen_ai.choice, ...)
  └─ Cycle <cycle-id> (event_loop.cycle_id, gen_ai.choice.tool.result, ...)
        └─ Model invoke (gen_ai.request.model, prompt/completion, token usage)
        └─ Tool: <tool name> (gen_ai.tool.name, gen_ai.tool.call.id, tool.status)
```

This demo runs the same travel agent from demo 01 (search a flight, check weather, book it) with tracing on, and walks the printed tree back to the `search_flights` → `get_weather` → `book_flight` calls it represents.

### What you'll see (real span names from an OpenAI `gpt-4o-mini` run)

Each span prints as JSON when it closes. The four documented levels appear exactly as named in the SDK's own span-naming code:

```
invoke_agent Strands Agents      # the whole run (top-level span)
  execute_event_loop_cycle       # one reasoning cycle
    chat                         # the model invocation for that cycle
    execute_tool search_flights  # one per tool call
    execute_tool get_weather
    execute_tool book_flight
```

The `invoke_agent` span's attributes carry the totals (`gen_ai.usage.total_tokens: 2725`, `gen_ai.request.model: "gpt-4o-mini"`); each `execute_tool` span carries that one call's `gen_ai.tool.name` and result. This is real output, not a mocked example — run the script yourself to see the full JSON.

---

## Why this design? (native-Strands choices)

| Choice | Why it's built this way |
|---|---|
| `StrandsTelemetry().setup_console_exporter()` | The documented [local development setup](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#7-local-development-setup): no collector needed to see spans. |
| `pip install 'strands-agents[otel]'` | The [Enabling Tracing](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#3-enabling-tracing) section's required extra. |
| Agent / Cycle / Model invoke / Tool spans | The exact hierarchy from [Trace Structure](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#4-trace-structure) — not a custom shape. |
| Optional OTLP export to a local Jaeger container | The documented [Local Development Setup](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#7-local-development-setup) recipe, for anyone who wants the visual UI instead of console lines. |

**Why Strands fits this well:** tracing is native, not bolted on — `StrandsTelemetry` wires up the OpenTelemetry SDK and registers it as the global tracer provider, so every subsequent `Agent(...)` call is automatically instrumented. There's no manual span-wrapping of your own agent loop.

---

## Captured attributes (from the docs, not invented)

Per the [Captured Attributes](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#5-captured-attributes) table, the Tool-Level span alone carries `tool.status`, `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.event.start_time`/`end_time`, and `gen_ai.choice` (the formatted tool result) — enough to answer "did `book_flight` fail, and what did it return" from the trace alone, without re-running anything.

---

## Quick Start

```bash
cd 02-opentelemetry-traces
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env   # then fill in OPENAI_API_KEY and DUFFEL_API_KEY
uv run python test_opentelemetry_traces.py
```

Want the visual Jaeger UI instead of console lines? Run a local collector first ([documented here](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#7-local-development-setup)):

```bash
docker run -d --name jaeger \
  -p 16686:16686 -p 4317:4317 -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

Then set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318` in `.env` and open [http://localhost:16686](http://localhost:16686) after running the script.

---

## File structure

```
02-opentelemetry-traces/
├── travel_tools.py                  # Same tools as demo 01 (search_flights, get_weather, book_flight)
├── test_opentelemetry_traces.py     # Enables StrandsTelemetry, runs the agent, walks the trace tree
├── test_opentelemetry_traces.ipynb  # Same story, step by step
├── requirements.txt
├── .env.example
└── README.md
```

---

## Cleanup

| Resource | What to do |
|---|---|
| **AWS resources** | None created. |
| **Local files** | `bookings.db` (SQLite); delete anytime. |
| **Local containers** | `docker rm -f jaeger` if you ran the optional Jaeger container. |
| **Local virtualenv** | `rm -rf .venv` if you want the space back. |
| **API cost** | A few cents of OpenAI tokens per run; Open-Meteo and Duffel sandbox are free. |

---

## Frequently asked questions

**Do I need a collector to see traces?**
No. `setup_console_exporter()` prints the full span tree to your terminal — no Jaeger, no OTLP endpoint required. Use `setup_otlp_exporter()` only when you want a real backend (Jaeger locally, or CloudWatch/X-Ray in production — see demo 04).

**How is this different from demo 01's metrics?**
`result.metrics.get_summary()` is a flat, post-hoc summary of one invocation. Traces are the actual timeline: which cycle called which model invocation, which one triggered which tool, in what order — a hierarchy, not a summary table.

**Does this only work with Strands or OpenAI?**
No. OpenTelemetry is a vendor-neutral standard; Strands' trace hierarchy (Agent → Cycle → Model → Tool spans) is a Strands-specific instrumentation of that standard. The concept of hierarchical tracing carries over to other agent frameworks.

---

## References

- [Strands Agents: Traces](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) · [Observability overview](https://strandsagents.com/docs/user-guide/observability-evaluation/observability/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)
- [OpenTelemetry](https://opentelemetry.io/) · [Jaeger](https://www.jaegertracing.io/)
- Previous: [01 - Agent Metrics](../01-agent-metrics/) · Next: [03 - Custom Trace Attributes](../03-custom-trace-attributes/)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING](../CONTRIBUTING.md) for more information.

---

## Security

If you discover a potential security issue in this project, notify AWS/Amazon Security via the [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public GitHub issue.

---

## License

This library is licensed under the MIT-0 License. See the [LICENSE](../LICENSE) file for details.
