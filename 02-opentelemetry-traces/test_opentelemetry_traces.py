"""OpenTelemetry Traces: the full Agent -> Cycle -> LLM -> Tool span tree.

Demo 01 showed result.metrics.get_summary() — a flat post-hoc summary. This demo turns on
Strands' native OpenTelemetry integration (StrandsTelemetry) and runs the SAME travel agent,
so you see the actual hierarchical execution: which cycle triggered which model invocation,
which invocation triggered which tool call, in order, with span attributes.

Docs: https://strandsagents.com/docs/user-guide/observability-evaluation/traces/
"""

import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel  # OpenAI-compatible interface via Strands SDK
from strands.telemetry import StrandsTelemetry

import travel_tools as T

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY not set. Get yours at https://platform.openai.com/api-keys "
        "and add it to a .env file."
    )

# Registers a global tracer provider. With OTEL_EXPORTER_OTLP_ENDPOINT unset, only the
# console exporter prints spans; set it in .env to also ship them to a real collector
# (e.g. the local Jaeger container from the README).
strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_console_exporter()
if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
    strands_telemetry.setup_otlp_exporter()

# Uncomment to use Amazon Bedrock instead (uses your AWS credentials, no OpenAI key):
# from strands.models import BedrockModel
# model = BedrockModel(model_id="global.anthropic.claude-sonnet-4-6")
model = OpenAIModel(model_id="gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are a travel assistant. Search flights, check the weather at the destination, "
    "and book the best option for the traveler without asking for confirmation. Be concise."
)

# Open-Meteo's forecast only covers the next ~16 days, so pick a near date at run time.
TRIP_DATE = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
TRIP_PROMPT = (
    f"Book a one-way flight from JFK to MIA on {TRIP_DATE} for John Doe, "
    "and tell me if he'll need a jacket."
)


def main() -> None:
    T.init_booking_db()
    # trace_attributes tags every span this agent produces (see demo 03 for a dynamic,
    # per-call version of this using hooks instead of a static dict).
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT,
                  tools=[T.search_flights, T.get_weather, T.book_flight],
                  trace_attributes={"session.id": "demo-02-opentelemetry-traces"})

    print("Running the agent with OpenTelemetry tracing on. Spans print below as they close.")
    print("=" * 80)
    result = agent(TRIP_PROMPT)
    print("=" * 80)
    print()
    print("Final response:")
    print(result.message["content"][0]["text"])

    print()
    print("Ground truth (SQLite ledger, independent of what the agent said):")
    import json
    print(json.dumps(T.query_booked_offers(), indent=2))


if __name__ == "__main__":
    main()
