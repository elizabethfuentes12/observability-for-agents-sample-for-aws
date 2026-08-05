"""Delete everything deploy_agentcore.py created, in reverse order.

Idempotent: silently skips resources that are already gone.
"""

from __future__ import annotations

import json
import os
import pathlib

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

REGION = os.environ.get("AWS_REGION", "us-east-1")

FLIGHT_BOOKINGS_TABLE = "FlightBookings"
LAMBDA_ROLE_NAME = "travel-agent-lambda-execution-role"
AGENTCORE_ROLE_NAME = "travel-agent-agentcore-execution-role"
LAMBDA_NAME_PREFIX = "travel-agent-"
GATEWAY_NAME = "TravelAgentGateway"
RUNTIME_NAME = "TravelAgentRuntime"

HERE = pathlib.Path(__file__).resolve().parent
TOOL_SCHEMAS = json.loads((HERE / "tool_schemas" / "tools.json").read_text())

session = boto3.session.Session(region_name=REGION)
account_id = session.client("sts").get_caller_identity()["Account"]

iam = session.client("iam")
dynamodb = session.client("dynamodb")
lambda_client = session.client("lambda")
agentcore_ctrl = session.client("bedrock-agentcore-control")
ecr = session.client("ecr")
codebuild = session.client("codebuild")
s3 = session.client("s3")


def _swallow_missing(fn, code="ResourceNotFoundException"):
    try:
        return fn()
    except ClientError as e:
        if e.response["Error"]["Code"] in (code, "NoSuchEntity", "NoSuchBucket", "404"):
            return None
        raise


print(f"→ Cleaning up in {REGION} for account {account_id}")

# 1. Delete AgentCore Runtime(s) by name
runtimes = agentcore_ctrl.list_agent_runtimes().get("items", [])
for rt in runtimes:
    if rt.get("agentRuntimeName") == RUNTIME_NAME or rt.get("name") == RUNTIME_NAME:
        rid = rt.get("agentRuntimeId") or rt.get("id")
        _swallow_missing(lambda: agentcore_ctrl.delete_agent_runtime(agentRuntimeId=rid))
        print(f"  ✓ Deleted runtime {RUNTIME_NAME}")
        break
else:
    print(f"  · No runtime named {RUNTIME_NAME}")

# 2. Delete gateway targets, then gateway
gateways = agentcore_ctrl.list_gateways().get("items", [])
for gw in gateways:
    if gw.get("name") != GATEWAY_NAME:
        continue
    gid = gw["gatewayId"]
    targets = agentcore_ctrl.list_gateway_targets(gatewayIdentifier=gid).get("items", [])
    for t in targets:
        _swallow_missing(lambda t=t: agentcore_ctrl.delete_gateway_target(
            gatewayIdentifier=gid, targetId=t["targetId"]))
        print(f"  ✓ Deleted gateway target {t['name']}")
    _swallow_missing(lambda: agentcore_ctrl.delete_gateway(gatewayIdentifier=gid))
    print(f"  ✓ Deleted gateway {GATEWAY_NAME}")
    break
else:
    print(f"  · No gateway named {GATEWAY_NAME}")

# 3. Delete the tool Lambdas
for schema in TOOL_SCHEMAS:
    fn_name = f"{LAMBDA_NAME_PREFIX}{schema['name']}"
    _swallow_missing(lambda: lambda_client.delete_function(FunctionName=fn_name))
    print(f"  ✓ Deleted Lambda {fn_name}")

# 4. Delete IAM roles (detach policies first)
for role_name in (LAMBDA_ROLE_NAME, AGENTCORE_ROLE_NAME):
    try:
        for p in iam.list_attached_role_policies(RoleName=role_name).get("AttachedPolicies", []):
            iam.detach_role_policy(RoleName=role_name, PolicyArn=p["PolicyArn"])
        for p in iam.list_role_policies(RoleName=role_name).get("PolicyNames", []):
            iam.delete_role_policy(RoleName=role_name, PolicyName=p)
        iam.delete_role(RoleName=role_name)
        print(f"  ✓ Deleted role {role_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            print(f"  · No role {role_name}")
        else:
            raise

# 5. Delete DynamoDB table
try:
    dynamodb.delete_table(TableName=FLIGHT_BOOKINGS_TABLE)
    print(f"  ✓ Deleted table {FLIGHT_BOOKINGS_TABLE}")
except ClientError as e:
    if e.response["Error"]["Code"] == "ResourceNotFoundException":
        print(f"  · No table {FLIGHT_BOOKINGS_TABLE}")
    else:
        raise

# 6. Delete ECR repo + CodeBuild project the starter toolkit created
ecr_repo = f"bedrock-agentcore-{RUNTIME_NAME.lower()}"
try:
    ecr.delete_repository(repositoryName=ecr_repo, force=True)
    print(f"  ✓ Deleted ECR repo {ecr_repo}")
except ClientError as e:
    if e.response["Error"]["Code"] != "RepositoryNotFoundException":
        raise
    print(f"  · No ECR repo {ecr_repo}")

codebuild_project = f"bedrock-agentcore-{RUNTIME_NAME.lower()}-builder"
try:
    codebuild.delete_project(name=codebuild_project)
    print(f"  ✓ Deleted CodeBuild project {codebuild_project}")
except ClientError as e:
    if e.response["Error"]["Code"] != "ResourceNotFoundException":
        raise
    print(f"  · No CodeBuild project {codebuild_project}")

# 7. Delete local .bedrock_agentcore*.yaml files
for f in HERE.glob(".bedrock_agentcore*.yaml"):
    f.unlink()
    print(f"  ✓ Removed local file {f.name}")

print("Cleanup complete.")
