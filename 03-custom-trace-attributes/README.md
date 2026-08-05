# Custom Trace Attributes: Tag Business Facts on Agent Spans

[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org) [![Strands Agents](https://img.shields.io/badge/Strands_Agents-1.47.0-blue.svg)](https://strandsagents.com/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) [![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-enabled-blueviolet.svg)](https://opentelemetry.io/) [![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991.svg?logo=openai)](https://platform.openai.com/)

> Demo 02 showed the trace tree Strands gives you automatically. This demo adds attributes that mean something to *your* business, not just to the SDK, onto that same tree.

---

## What does this demo show?

Out of the box, Strands trace spans carry technical attributes: `gen_ai.tool.name`, `gen_ai.usage.total_tokens`, `tool.status`. None of those tell you *"was this a high-value booking?"* — that context is yours to add.

The [traces guide](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) documents two ways to do it:

1. **Agent-level `trace_attributes`** ([Custom Attribute Tracking](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#82-custom-attribute-tracking)) — attach static metadata (session id, user id, tags) to every span the agent produces:

   ```python
   agent = Agent(
       tools=[search_flights, get_weather, book_flight],
       trace_attributes={"session.id": "abc-1234"},
   )
   ```

2. **A hook that tags the ACTIVE span at the moment a business rule fires** — an `AfterToolCallEvent` callback ([Result Modification pattern](https://strandsagents.com/docs/user-guide/concepts/agents/hooks/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#53-result-modification)) that reaches the currently-open `execute_tool` span with `trace.get_current_span()` (the [Custom Spans](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#83-custom-spans) API, applied to an existing span instead of creating a new one) and calls `span.set_attribute(...)` directly.

This demo runs the travel agent from demos 01–02 with a `TagVipBookings` hook: when `book_flight`'s amount crosses `VIP_THRESHOLD` (set low, $50, so the Duffel sandbox fares actually cross it), the hook tags that exact call's `execute_tool book_flight` span with `business.vip_booking=true` and `business.booking_amount_usd=<amount>`. The trace then answers a question no SDK attribute can: not "did the tool succeed" but "was this booking one the business cares about."

### What you'll see (real span attributes from an OpenAI `gpt-4o-mini` run)

```json
{
  "name": "execute_tool book_flight",
  "attributes": {
    "gen_ai.tool.name": "book_flight",
    "gen_ai.tool.status": "success",
    "business.booking_amount_usd": 88.73,
    "business.vip_booking": true
  }
}
```

`business.booking_amount_usd` and `business.vip_booking` sit right alongside the SDK's own `gen_ai.tool.*` attributes on the SAME span — added by the hook, not the SDK.

---

## Why this design? (native-Strands choices)

| Choice | Why it's built this way |
|---|---|
| `trace_attributes` at agent creation | The documented mechanism for attaching static context (session, user, tags) to every span — [Custom Attribute Tracking](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#82-custom-attribute-tracking). |
| `AfterToolCallEvent` hook for a dynamic tag | Static `trace_attributes` can't express "only when the amount crosses a threshold" — that needs a hook reacting to the actual tool call, per the [hooks cookbook](https://strandsagents.com/docs/user-guide/concepts/agents/hooks/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el). |
| `trace.get_current_span()` inside the hook | Strands keeps the `execute_tool` span active (via `trace_api.use_span`) for the tool call's whole duration, including while `AfterToolCallEvent` fires — confirmed by reading the installed SDK's `tools/executors/_executor.py`. So the hook tags the REAL tool-call span, not a new one. |
| No injected failure, no fallback simulation | This series shows visibility into an agent's *normal* behavior; a real threshold on a real booking amount is a genuine business signal, not a simulated chaos effect. |

---

## Quick Start

```bash
cd 03-custom-trace-attributes
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env   # then fill in OPENAI_API_KEY and DUFFEL_API_KEY
uv run python test_custom_trace_attributes.py
```

---

## File structure

```
03-custom-trace-attributes/
├── travel_tools.py                       # Same tools as demos 01-02
├── test_custom_trace_attributes.py       # trace_attributes + TagVipBookings (AfterToolCallEvent) hook
├── test_custom_trace_attributes.ipynb    # Same story, step by step
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
| **Local virtualenv** | `rm -rf .venv` if you want the space back. |
| **API cost** | A few cents of OpenAI tokens per run; Open-Meteo and Duffel sandbox are free. |

---

## Frequently asked questions

**Why not just add a business field to the tool's return value instead of a trace attribute?**
The tool's return value goes to the model — it becomes tokens the LLM reads and can hallucinate about. A trace attribute is out-of-band: it's visible to whoever reads your traces (an ops dashboard, a data pipeline) without adding a single token to the agent's context.

**Do custom attributes cost extra tokens?**
No. They're OpenTelemetry span metadata, entirely separate from the message list the model sees.

**Does this only work with Strands or OpenAI?**
No. Attaching business context to a trace span is a general OpenTelemetry concept (`span.set_attribute`); Strands exposes it at both the agent level (`trace_attributes`) and per-event level (hooks + custom spans).

---

## References

- [Strands Agents: Traces — Custom Attribute Tracking](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#82-custom-attribute-tracking) · [Custom Spans](https://strandsagents.com/docs/user-guide/observability-evaluation/traces/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#83-custom-spans)
- [Strands Agents: Hooks — Result Modification](https://strandsagents.com/docs/user-guide/concepts/agents/hooks/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el#53-result-modification)
- Previous: [02 - OpenTelemetry Traces](../02-opentelemetry-traces/) · Next: [04 - AgentCore Observability](../04-agentcore-observability/)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING](../CONTRIBUTING.md) for more information.

---

## Security

If you discover a potential security issue in this project, notify AWS/Amazon Security via the [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public GitHub issue.

---

## License

This library is licensed under the MIT-0 License. See the [LICENSE](../LICENSE) file for details.
