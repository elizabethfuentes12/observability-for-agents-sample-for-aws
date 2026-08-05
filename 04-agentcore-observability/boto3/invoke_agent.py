"""Invoke the deployed travel agent N times, each with a different session ID.

Use this to generate real observability data — multiple sessions, multiple traces —
so there's something to explore in CloudWatch GenAI Observability (Agents View,
Sessions View, Traces View).

Usage:
    uv run python invoke_agent.py                 # 5 invocations (default)
    uv run python invoke_agent.py --count 10      # 10 invocations
"""

from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timedelta

import boto3
from dotenv import load_dotenv

load_dotenv()

REGION = os.environ.get("AWS_REGION", "us-east-1")
RUNTIME_NAME = "TravelAgentRuntime"

# A varied set of realistic travel questions, so the traces differ: some book,
# some only search, some only ask for weather — different tool paths per session.
PROMPT_TEMPLATES = [
    "Book a one-way flight from JFK to MIA on {date} for John Doe, and tell me if he'll need a jacket.",
    "What's the weather like in Miami on {date}? Just the forecast, please.",
    "Find me flight options from LAX to SEA on {date}. Don't book anything yet.",
    "Book the cheapest flight from BOS to ORD on {date} for Maria Garcia.",
    "I'm flying from SFO to DEN on {date}. What should I pack, and how much are flights?",
    "Search flights from ATL to AUS on {date} and book the fastest one for Alex Kim.",
    "Compare flight prices from SEA to PHX on {date}. Which airline is cheapest?",
    "Book JFK to LAX on {date} for Sam Rivera and check the weather in Los Angeles that day.",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Number of invocations (default 5)")
    args = parser.parse_args()

    session = boto3.session.Session(region_name=REGION)
    ctrl = session.client("bedrock-agentcore-control")
    rt = session.client("bedrock-agentcore")

    # Resolve the runtime ARN by name, so the script works after any redeploy.
    runtimes = ctrl.list_agent_runtimes().get("agentRuntimes", [])
    arn = None
    for r in runtimes:
        if r.get("agentRuntimeName") == RUNTIME_NAME:
            arn = r["agentRuntimeArn"]
            break
    if not arn:
        raise SystemExit(f"No runtime named {RUNTIME_NAME} found in {REGION}.")

    print(f"→ Runtime: {arn}")
    print(f"→ Invoking {args.count} times, each with a fresh session ID\n")

    trip_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

    for i in range(args.count):
        prompt = PROMPT_TEMPLATES[i % len(PROMPT_TEMPLATES)].format(date=trip_date)
        session_id = f"video-demo-{uuid.uuid4()}"

        print(f"[{i + 1}/{args.count}] session: {session_id}")
        print(f"    prompt: {prompt[:90]}")
        response = rt.invoke_agent_runtime(
            agentRuntimeArn=arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": prompt}).encode("utf-8"),
        )
        body = response["response"].read().decode("utf-8")
        print(f"    response: {body[:120]}...\n")

    print("Done. Open CloudWatch → GenAI Observability:")
    print("  · Agents View   — TravelAgentRuntime with its invocation metrics")
    print("  · Sessions View — one session per invocation above")
    print("  · Traces View   — one trace per invocation, with the full span tree")


if __name__ == "__main__":
    main()
