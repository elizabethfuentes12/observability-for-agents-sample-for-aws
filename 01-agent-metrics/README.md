# Agent Metrics: What You Get With Zero Extra Configuration

[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org) [![Strands Agents](https://img.shields.io/badge/Strands_Agents-1.47.0-blue.svg)](https://strandsagents.com/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) [![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991.svg?logo=openai)](https://platform.openai.com/) [![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-FF9900.svg)](https://aws.amazon.com/bedrock/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)

> **Start here.** This demo runs a travel agent doing its normal job — no injected failures, no chaos effects — and looks at the SAME run through two lenses: traditional logging, and the Strands SDK's built-in `EventLoopMetrics`.

> Uses **Strands Agents**. Reasoning steps, tool-call cascades, and token cost per cycle are general agent-observability concepts; the same patterns carry over to other agent frameworks.

---

## What does this demo show?

The [Strands observability guide](https://strandsagents.com/docs/user-guide/observability-evaluation/observability/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) states the core idea this whole series is built on:

> "We leverage the same fundamental building blocks as traditional software — **traces**, **metrics**, and **logs** — [but] their application to agents requires special consideration. We need to capture not only standard application telemetry but also AI-specific signals like model interactions, reasoning steps, and tool usage."

This demo books one real flight (Duffel sandbox), checks the weather (Open-Meteo), and looks at what each lens shows about the SAME run:

| Lens | What it gives you | Setup |
|---|---|---|
| **Traditional logging** (`logging.getLogger("strands")`) | Lines like `tool_use=<...> \| streaming` — useful for "did this run", not for "how much did it cost" | Already in the SDK; just set a log level |
| **`result.metrics.get_summary()`** (`EventLoopMetrics`) | Token usage, cycle count, per-tool call counts/timings, a nested trace tree | Already in the SDK; **zero extra install, zero extra config** |

### What you'll see (real output from an OpenAI `gpt-4o-mini` run)

```
LENS 1 — traditional logging
DEBUG | strands.tools.executors._executor | tool_use=<...name': 'search_flights'...> | streaming
DEBUG | strands.tools.executors._executor | tool_use=<...name': 'get_weather'...> | streaming
DEBUG | strands.tools.executors._executor | tool_use=<...name': 'book_flight'...> | streaming
John Doe's flight from JFK to MIA has been successfully booked ... booking reference BK-JSFPJ5 ...

LENS 2 — result.metrics.get_summary()
{
  "total_cycles": 3,
  "total_duration_s": 5.13,
  "accumulated_usage": {"inputTokens": 2520, "outputTokens": 209, "totalTokens": 2729},
  "tool_usage": {
    "search_flights": {"call_count": 1, "success_count": 1, "average_time_s": 0.721},
    "get_weather":     {"call_count": 1, "success_count": 1, "average_time_s": 1.434},
    "book_flight":     {"call_count": 1, "success_count": 1, "average_time_s": 0.006}
  }
}

Ground truth (SQLite ledger): [{"booking_reference": "BK-FLSXWE", "passenger": "John Doe", ...}]
```

The logging lens tells you the agent called three tools and produced a final answer. The metrics lens tells you it took **3 event-loop cycles**, **2,729 tokens**, and exactly how long each tool call took — the questions "how much did this cost" and "is this tool slow" that a log line can't answer.

---

## Why this design? (native-Strands choices)

| Choice | Why it's built this way |
|---|---|
| `logging.getLogger("strands").setLevel(logging.DEBUG)` | The exact pattern from the [logs guide](https://strandsagents.com/docs/user-guide/observability-evaluation/logs/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el): "each module creates its own logger... all loggers are children of the 'strands' root logger." |
| `result.metrics.get_summary()` | The [metrics guide](https://strandsagents.com/docs/user-guide/observability-evaluation/metrics/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)'s own example: "a convenient `get_summary()` method... that gives you a comprehensive overview of your agent's performance in a single call." |
| No `StrandsTelemetry`, no OTEL | Metrics and local execution traces are collected automatically by the SDK — [Traces](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) (OpenTelemetry export) is deliberately the *next* demo, not this one. |
| Real Duffel + Open-Meteo calls | So the demo measures a real agent doing real work, not a mocked response. |

**Why Strands fits this well:** every `Agent(...)` call already accumulates `EventLoopMetrics` — cycle counts, token usage, per-tool statistics — with no configuration. You don't have to choose to be observable; `pip install strands-agents` and `result.metrics` already exist on the object your agent call returns.

---

## Honest note: `accumulated_metrics.latencyMs` reads 0

Read directly from the installed SDK source (`strands/models/openai.py`, `anthropic.py`, `litellm.py`, `gemini.py` — 1.47.0): each of these providers ships `"latencyMs": 0,  # TODO` in their streaming-metrics code. This is a known, provider-side gap in the current SDK — not something this demo works around, and not a "resilience" fix (that would dilute this series' thesis; see the sibling repo for that pattern). The metric that IS accurate everywhere is `accumulated_usage` (real token counts) and per-tool `average_time_s`, which the summary above already uses. `ollama.py`, `mistral.py`, and `llamacpp.py` do report a real `latencyMs`, if you switch providers.

---

## Quick Start

```bash
cd 01-agent-metrics
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env   # then fill in OPENAI_API_KEY and DUFFEL_API_KEY
uv run python test_agent_metrics.py
```

> A free Duffel **sandbox** token is at [app.duffel.com](https://app.duffel.com): **More → Developers → Access tokens** (test mode). Open-Meteo needs no key.
>
> The trip date is computed at run time (`today + 5 days`) so it always falls inside Open-Meteo's ~16-day forecast window.

---

## File structure

```
01-agent-metrics/
├── travel_tools.py          # search_flights (Duffel), get_weather (Open-Meteo), book_flight (SQLite ledger)
├── test_agent_metrics.py    # Runs the agent under both lenses: logging vs metrics.get_summary()
├── requirements.txt
├── .env.example
└── README.md
```

The booking database `bookings.db` is created locally at run time and is git-ignored.

---

## Cleanup

| Resource | What to do |
|---|---|
| **AWS resources** | None created; this demo calls model inference and two public APIs. |
| **Local files** | `bookings.db` (SQLite); delete anytime (`rm bookings.db`). |
| **Local virtualenv** | `rm -rf .venv` if you want the space back. |
| **API cost** | A few cents of OpenAI tokens per run; Open-Meteo and Duffel sandbox are free. |

---

## Frequently asked questions

**What's the difference between logs and metrics for an AI agent?**
Logs are timestamped text records of what happened ("tool X was called"). Metrics are measurements of those events (how many times, how long, how many tokens) — see the [observability overview](https://strandsagents.com/docs/user-guide/observability-evaluation/observability/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el). Both matter; a log tells you *that* something happened, a metric tells you *how much* it cost.

**Do I need to install anything extra for `result.metrics`?**
No. It's part of `strands-agents` itself — no `[otel]` extra, no exporter, no collector. Traces with OpenTelemetry export are a separate, later step (see the next demo).

**Does this only work with Strands or OpenAI?**
No. Reasoning steps, tool-call cascades, and per-invocation cost are general agent concepts. This demo uses Strands Agents and defaults to OpenAI `gpt-4o-mini`; switch to Amazon Bedrock by editing the model block at the top of `test_agent_metrics.py`.

---

## References

- [Strands Agents: Observability overview](https://strandsagents.com/docs/user-guide/observability-evaluation/observability/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) · [Metrics](https://strandsagents.com/docs/user-guide/observability-evaluation/metrics/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) · [Logs](https://strandsagents.com/docs/user-guide/observability-evaluation/logs/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el)
- [Open-Meteo](https://open-meteo.com) · [Duffel](https://duffel.com) · tools adapted from [Ricardo Ceci's `curso-strands-agentcore-2026`](https://github.com/ricardoceci/curso-strands-agentcore-2026)
- Next: [02 - OpenTelemetry Traces](../02-opentelemetry-traces/)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING](../CONTRIBUTING.md) for more information.

---

## Security

If you discover a potential security issue in this project, notify AWS/Amazon Security via the [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public GitHub issue.

---

## License

This library is licensed under the MIT-0 License. See the [LICENSE](../LICENSE) file for details.
