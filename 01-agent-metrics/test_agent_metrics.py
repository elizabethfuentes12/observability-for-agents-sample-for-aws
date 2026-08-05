"""Agent Metrics: what the Strands Agents SDK gives you with zero extra configuration.

Runs a travel agent doing its normal job (search a flight, check the weather, book it) and
compares two views of the SAME run:

1. Traditional logging (`logging.getLogger("strands")`) — the pattern from the Strands docs'
   "logs" guide. You get lines like "tool_use=<...> | streaming"; useful, but it does not tell
   you how many tokens the run cost or how many reasoning cycles it took.
2. `result.metrics.get_summary()` — the SDK's built-in `EventLoopMetrics`, from the Strands docs'
   "metrics" guide. No install beyond `strands-agents`, no OpenTelemetry setup: token usage,
   cycle count, per-tool call counts and timings, and a nested trace tree are already on the
   `AgentResult` your agent call returns.

Docs: https://strandsagents.com/docs/user-guide/observability-evaluation/logs/
      https://strandsagents.com/docs/user-guide/observability-evaluation/metrics/
"""

import json
import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel  # OpenAI-compatible interface via Strands SDK

import travel_tools as T

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY not set. Get yours at https://platform.openai.com/api-keys "
        "and add it to a .env file."
    )

# Uncomment to use Amazon Bedrock instead (uses your AWS credentials, no OpenAI key):
# from strands.models import BedrockModel
# model = BedrockModel(model_id="global.anthropic.claude-sonnet-4-6")
model = OpenAIModel(model_id="gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are a travel assistant. Search flights, check the weather at the destination, "
    "and book the best option for the traveler without asking for confirmation. Be concise."
)

# Open-Meteo's forecast only covers the next ~16 days, so pick a near date at run time
# rather than a fixed one that will eventually fall outside that window.
TRIP_DATE = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
TRIP_PROMPT = (
    f"Book a one-way flight from JFK to MIA on {TRIP_DATE} for John Doe, "
    "and tell me if he'll need a jacket."
)


def run_with_traditional_logging() -> None:
    """The logging.getLogger("strands") pattern from the Strands docs' logs guide."""
    logging.getLogger("strands").setLevel(logging.DEBUG)
    logging.basicConfig(
        format="%(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
        force=True,
    )
    T.init_booking_db()
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT,
                  tools=[T.search_flights, T.get_weather, T.book_flight])
    agent(TRIP_PROMPT)
    logging.getLogger("strands").setLevel(logging.WARNING)


def run_with_metrics_summary() -> dict:
    """Zero extra config: result.metrics.get_summary() from the Strands docs' metrics guide."""
    T.init_booking_db()
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT,
                  tools=[T.search_flights, T.get_weather, T.book_flight])
    result = agent(TRIP_PROMPT)
    return result.metrics.get_summary()


def main() -> None:
    print("=" * 80)
    print("LENS 1 — traditional logging (logging.getLogger('strands'))")
    print("=" * 80)
    run_with_traditional_logging()

    print()
    print("=" * 80)
    print("LENS 2 — result.metrics.get_summary() (Strands EventLoopMetrics)")
    print("=" * 80)
    summary = run_with_metrics_summary()
    print(json.dumps({
        "total_cycles": summary["total_cycles"],
        "total_duration_s": round(summary["total_duration"], 2),
        "accumulated_usage": summary["accumulated_usage"],
        "accumulated_metrics": summary["accumulated_metrics"],
        "tool_usage": {
            name: {"call_count": data["execution_stats"]["call_count"],
                   "success_count": data["execution_stats"]["success_count"],
                   "average_time_s": round(data["execution_stats"]["average_time"], 3)}
            for name, data in summary.get("tool_usage", {}).items()
        },
    }, indent=2))

    print()
    print("Ground truth (SQLite ledger, independent of what the agent said):")
    print(json.dumps(T.query_booked_offers(), indent=2))


if __name__ == "__main__":
    main()
