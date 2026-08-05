"""TravelAgentObservabilityStack — one-command deploy of the whole system.

Resources created:
  - DynamoDB table `FlightBookings` (RemovalPolicy.DESTROY)
  - IAM role for AgentCore Runtime
  - AgentCore Gateway (MCP) + 3 tool Lambdas + gateway targets
  - AgentCore Runtime pointing at the agent zip in S3

All resources use RemovalPolicy.DESTROY so `cdk destroy` leaves nothing behind.
"""

import os
import pathlib

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct

from agentcore import AgentCoreGateway, AgentCoreRole, AgentCoreRuntime


class TravelAgentObservabilityStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        gateway_name = "TravelAgentGateway"
        runtime_name = "TravelAgentRuntime"
        agentcore_role_name = "TravelAgentAgentCoreRole"
        model_id = self.node.try_get_context("bedrock_model_id") or "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

        duffel_api_key = os.environ.get("DUFFEL_API_KEY")
        if not duffel_api_key:
            raise RuntimeError(
                "DUFFEL_API_KEY environment variable is required for cdk deploy. "
                "Get a free sandbox token at https://app.duffel.com and export it before deploying.")

        # DynamoDB table used by book_flight.
        flight_bookings = dynamodb.Table(
            self,
            "FlightBookings",
            table_name="FlightBookings",
            partition_key=dynamodb.Attribute(
                name="booking_reference", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # IAM execution role for the AgentCore Runtime.
        agentcore_role = AgentCoreRole(
            self,
            "AgentCoreRole",
            role_name=agentcore_role_name,
            tool_lambda_name_prefix="travel-agent-",
        )

        # Gateway + 3 tool Lambdas + gateway targets.
        gateway = AgentCoreGateway(
            self,
            "TravelAgentGateway",
            gateway_name=gateway_name,
            agentcore_role=agentcore_role.role,
            flight_bookings_table=flight_bookings,
            duffel_api_key=duffel_api_key,
            tool_lambda_name_prefix="travel-agent-",
        )

        # Runtime.
        here = pathlib.Path(__file__).resolve().parent
        deployment_zip = str(here / "agent_files" / "deployment_package.zip")
        if not pathlib.Path(deployment_zip).exists():
            raise RuntimeError(
                f"Deployment package not found at {deployment_zip}. "
                "Run `./create_deployment_package.sh` before `cdk deploy`.")

        runtime = AgentCoreRuntime(
            self,
            "TravelAgentRuntime",
            runtime_name=runtime_name,
            agentcore_role=agentcore_role.role,
            gateway_url=gateway.gateway.attr_gateway_url,
            model_id=model_id,
            deployment_zip_path=deployment_zip,
        )

        CfnOutput(self, "AgentRuntimeArn", value=runtime.runtime.attr_agent_runtime_arn)
        CfnOutput(self, "GatewayUrl", value=gateway.gateway.attr_gateway_url)
        CfnOutput(self, "FlightBookingsTableName", value=flight_bookings.table_name)
