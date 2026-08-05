"""Step-by-step boto3 deployment of the travel agent to AgentCore Runtime.

Runtime-only architecture: the agent's three tools (search_flights, get_weather,
book_flight) live inside the agent code. book_flight writes to DynamoDB.

Steps:
  1. Create DynamoDB table `FlightBookings`
  2. Create the AgentCore Runtime execution IAM role
  3. Deploy the runtime with the bedrock-agentcore-starter-toolkit
  4. Invoke once as a smoke test

Idempotent: safe to re-run — resources already present are reused instead of failing.
"""

from __future__ import annotations

import json
import os
import pathlib
import time

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------- config

REGION = os.environ.get("AWS_REGION", "us-east-1")
DUFFEL_API_KEY = os.environ.get("DUFFEL_API_KEY")
if not DUFFEL_API_KEY:
    raise SystemExit("DUFFEL_API_KEY is required. Get a free sandbox token at https://app.duffel.com")

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")

FLIGHT_BOOKINGS_TABLE = "FlightBookings"
AGENTCORE_ROLE_NAME = "travel-agent-agentcore-execution-role"
RUNTIME_NAME = "TravelAgentRuntime"

HERE = pathlib.Path(__file__).resolve().parent

session = boto3.session.Session(region_name=REGION)
account_id = session.client("sts").get_caller_identity()["Account"]

iam_client = session.client("iam")
dynamodb_client = session.client("dynamodb")

print(f"→ Region: {REGION}")
print(f"→ Account: {account_id}")
print(f"→ Model: {MODEL_ID}")
print()

# --------------------------------------------------------------------------- 1. DynamoDB

print("Step 1: DynamoDB table")
try:
    dynamodb_client.create_table(
        TableName=FLIGHT_BOOKINGS_TABLE,
        KeySchema=[{"AttributeName": "booking_reference", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "booking_reference", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    print(f"  ✓ Created {FLIGHT_BOOKINGS_TABLE}")
    waiter = dynamodb_client.get_waiter("table_exists")
    waiter.wait(TableName=FLIGHT_BOOKINGS_TABLE)
except ClientError as e:
    if e.response["Error"]["Code"] == "ResourceInUseException":
        print(f"  ✓ {FLIGHT_BOOKINGS_TABLE} already exists (reusing)")
    else:
        raise
print()

# --------------------------------------------------------------------------- 2. IAM role

print("Step 2: AgentCore execution role")


def _get_or_create_role(role_name: str, assume_service: str, description: str) -> str:
    try:
        role = iam_client.get_role(RoleName=role_name)
        print(f"  ✓ {role_name} already exists (reusing)")
        return role["Role"]["Arn"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise
    assume_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": assume_service},
            "Action": "sts:AssumeRole",
        }],
    }
    role = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_policy),
        Description=description,
    )
    print(f"  ✓ Created {role_name}")
    return role["Role"]["Arn"]


agentcore_role_arn = _get_or_create_role(
    AGENTCORE_ROLE_NAME, "bedrock-agentcore.amazonaws.com",
    "Execution role for the travel-agent AgentCore Runtime")
iam_client.put_role_policy(
    RoleName=AGENTCORE_ROLE_NAME,
    PolicyName="AgentCoreRuntimeAccess",
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow",
             "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
             "Resource": "*"},
            # book_flight writes to the FlightBookings table from inside the runtime.
            {"Effect": "Allow",
             "Action": ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan"],
             "Resource": f"arn:aws:dynamodb:{REGION}:{account_id}:table/{FLIGHT_BOOKINGS_TABLE}"},
            {"Effect": "Allow",
             "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
             "Resource": "*"},
            # The runtime pulls its container image from ECR at startup.
            {"Effect": "Allow",
             "Action": ["ecr:GetAuthorizationToken"],
             "Resource": "*"},
            {"Effect": "Allow",
             "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
             "Resource": f"arn:aws:ecr:{REGION}:{account_id}:repository/bedrock-agentcore-*"},
            # OTEL traces/metrics from ADOT auto-instrumentation land in X-Ray + CloudWatch.
            {"Effect": "Allow",
             "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords",
                         "cloudwatch:PutMetricData"],
             "Resource": "*"},
        ],
    }))

print("  → Waiting 10s for IAM role propagation")
time.sleep(10)
print()

# --------------------------------------------------------------------------- 3. Runtime via starter toolkit

print("Step 3: AgentCore Runtime (via bedrock-agentcore-starter-toolkit)")

try:
    from bedrock_agentcore_starter_toolkit import Runtime
except ImportError:
    raise SystemExit(
        "bedrock-agentcore-starter-toolkit is not installed. "
        "Run: uv pip install -r requirements.txt")

runtime = Runtime()
runtime.configure(
    entrypoint="travel_agent.py",
    execution_role=agentcore_role_arn,
    agent_name=RUNTIME_NAME,
    requirements_file="agent_requirements.txt",
    region=REGION,
    auto_create_ecr=True,
)
# Env vars are passed at launch time (Runtime.launch signature), not configure time.
launch = runtime.launch(env_vars={
    "BEDROCK_MODEL_ID": MODEL_ID,
    "FLIGHT_BOOKINGS_TABLE": FLIGHT_BOOKINGS_TABLE,
    "DUFFEL_API_KEY": DUFFEL_API_KEY,
})

# launch() returns a LaunchResult object (fields: agent_arn, agent_id, ecr_uri, ...).
agent_runtime_arn = launch.agent_arn
print(f"  ✓ Runtime ready: {agent_runtime_arn}")
print()

# --------------------------------------------------------------------------- 4. Smoke test

print("Step 4: Smoke-test invocation")
agentcore_rt = session.client("bedrock-agentcore")
response = agentcore_rt.invoke_agent_runtime(
    agentRuntimeArn=agent_runtime_arn,
    payload=json.dumps({"prompt": "What tools do you have available?"}).encode("utf-8"),
)
body = response["response"].read().decode("utf-8")
print(f"  agent responded: {body[:500]}")
print()

print("Deploy complete.")
print(f"→ Agent Runtime ARN: {agent_runtime_arn}")
print(f"→ Bookings table:    {FLIGHT_BOOKINGS_TABLE}")
print()
print("Now open CloudWatch → GenAI Observability in the AWS console to see traces, "
      "sessions, and metrics for this agent.")
