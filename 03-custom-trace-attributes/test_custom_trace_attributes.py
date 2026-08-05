"""Custom Trace Attributes: tagging a business decision, not just a technical one.

Demo 02 showed the trace tree Strands gives you automatically (Agent -> Cycle -> Model -> Tool
spans). This demo adds attributes that mean something to a business, not just to the SDK, onto
that same tree, two ways:

1. `trace_attributes` at Agent creation — a STATIC tag applied to every span (e.g. a session id).
2. An `AfterToolCallEvent` hook — a DYNAMIC tag applied only when a business rule fires at
   runtime (here: `book_flight` for over $VIP_THRESHOLD gets `business.vip_booking=True` on
   the exact `execute_tool book_flight` span, using the documented Custom Spans API to reach
   the currently active span from inside the hook).

Docs: https://strandsagents.com/docs/user-guide/observability-evaluation/traces/#82-custom-attribute-tracking
      https://strandsagents.com/docs/user-guide/observability-evaluation/traces/#83-custom-spans
      https://strandsagents.com/docs/user-guide/concepts/agents/hooks/#53-result-modification
"""

import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from opentelemetry import trace
from strands import Agent
from strands.hooks import AfterToolCallEvent, HookProvider, HookRegistry
from strands.models.openai import OpenAIModel  # OpenAI-compatible interface via Strands SDK
from strands.telemetry import StrandsTelemetry

import travel_tools as T

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY not set. Get yours at https://platform.openai.com/api-keys "
        "and add it to a .env file."
    )

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_console_exporter()

# Uncomment to use Amazon Bedrock instead (uses your AWS credentials, no OpenAI key):
# from strands.models import BedrockModel
# model = BedrockModel(model_id="global.anthropic.claude-sonnet-4-6")
model = OpenAIModel(model_id="gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are a travel assistant. Search flights, check the weather at the destination, "
    "and book the best option for the traveler without asking for confirmation. Be concise."
)

TRIP_DATE = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
TRIP_PROMPT = (
    f"Book a one-way flight from JFK to MIA on {TRIP_DATE} for John Doe, "
    "and tell me if he'll need a jacket."
)

VIP_THRESHOLD = 50.0  # USD; low on purpose so the Duffel sandbox demo actually crosses it


class TagVipBookings(HookProvider):
    """Tags the ACTIVE `execute_tool book_flight` span with a business fact at runtime.

    `AfterToolCallEvent` fires while that tool's span is still the current OpenTelemetry span
    (Strands keeps it active for the duration of the tool call via `trace_api.use_span`), so
    `trace.get_current_span()` here returns that exact span — the documented Custom Spans
    pattern, applied to an existing span instead of creating a new one.
    """

    def __init__(self, threshold: float):
        self.threshold = threshold
        self.tagged = 0

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(AfterToolCallEvent, self._tag_if_vip)

    def _tag_if_vip(self, event: AfterToolCallEvent) -> None:
        if event.tool_use.get("name") != "book_flight":
            return
        amount = float(event.tool_use.get("input", {}).get("amount", 0))
        span = trace.get_current_span()
        is_vip = amount >= self.threshold
        span.set_attribute("business.booking_amount_usd", amount)
        span.set_attribute("business.vip_booking", is_vip)
        if is_vip:
            self.tagged += 1


def main() -> None:
    T.init_booking_db()
    vip_hook = TagVipBookings(threshold=VIP_THRESHOLD)
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT,
                  tools=[T.search_flights, T.get_weather, T.book_flight],
                  trace_attributes={"session.id": "demo-03-custom-trace-attributes"},
                  hooks=[vip_hook])

    print(f"Running the agent. VIP threshold: ${VIP_THRESHOLD:.2f}. Spans print below.")
    print("=" * 80)
    result = agent(TRIP_PROMPT)
    print("=" * 80)
    print()
    print(f"Bookings tagged business.vip_booking=True this run: {vip_hook.tagged}")
    print()
    print("Final response:")
    print(result.message["content"][0]["text"])

    print()
    print("Ground truth (SQLite ledger, independent of what the agent said):")
    print(json.dumps(T.query_booked_offers(), indent=2))


if __name__ == "__main__":
    main()
