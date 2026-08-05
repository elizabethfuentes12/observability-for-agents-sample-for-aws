"""AgentCore Gateway + one Lambda per tool.

Reads ../tool_schemas/tools.json, and for each entry creates:
  - a Python 3.11 Lambda with source from ../lambda_tools/<name>/
  - a CfnGatewayTarget wiring that Lambda to the MCP gateway

Property class names verified against aws-cdk-lib's aws_bedrockagentcore module
(GatewayProtocolConfigurationProperty, McpTargetConfigurationProperty, etc.).
"""

import json
import pathlib

from aws_cdk import Duration, Stack
from aws_cdk import aws_bedrockagentcore as agentcore
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class AgentCoreGateway(Construct):
    """MCP gateway backed by one Lambda per tool. Registers each tool as a gateway target."""

    def __init__(self, scope: Construct, construct_id: str, *,
                 gateway_name: str,
                 agentcore_role: iam.IRole,
                 flight_bookings_table: dynamodb.ITable,
                 duffel_api_key: str,
                 tool_lambda_name_prefix: str = "travel-agent-",
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stack = Stack.of(self)
        here = pathlib.Path(__file__).resolve().parent.parent  # cdk/
        schemas_path = here / "tool_schemas" / "tools.json"
        lambda_root = here / "lambda_tools"

        tool_schemas = json.loads(schemas_path.read_text())

        # Shared Lambda execution role: CloudWatch logs + selective DynamoDB access.
        lambda_role = iam.Role(
            self,
            "ToolLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"),
            ],
        )
        flight_bookings_table.grant_read_write_data(lambda_role)

        # The AgentCore Gateway itself.
        self.gateway = agentcore.CfnGateway(
            self,
            "Gateway",
            name=gateway_name,
            protocol_type="MCP",
            authorizer_type="NONE",
            role_arn=agentcore_role.role_arn,
            description="Travel agent tool gateway",
            protocol_configuration=agentcore.CfnGateway.GatewayProtocolConfigurationProperty(
                mcp=agentcore.CfnGateway.MCPGatewayConfigurationProperty(
                    instructions=("Travel agent tools: search flights via Duffel sandbox, "
                                   "check weather via Open-Meteo, book flights to DynamoDB."),
                    search_type="SEMANTIC",
                    supported_versions=["2025-03-26"],
                )
            ),
        )

        # For each tool in tools.json, create a Lambda + a Gateway target that binds it.
        for schema in tool_schemas:
            tool_name = schema["name"]
            fn_name = f"{tool_lambda_name_prefix}{tool_name}"
            source_dir = str(lambda_root / tool_name)

            fn = _lambda.Function(
                self,
                f"{tool_name}Function",
                function_name=fn_name,
                runtime=_lambda.Runtime.PYTHON_3_11,
                architecture=_lambda.Architecture.ARM_64,
                handler="lambda_function.handler",
                code=_lambda.Code.from_asset(source_dir),
                timeout=Duration.seconds(30),
                memory_size=256,
                role=lambda_role,
                environment={
                    "FLIGHT_BOOKINGS_TABLE": flight_bookings_table.table_name,
                    "DUFFEL_API_KEY": duffel_api_key,
                },
            )

            fn.add_permission(
                "AgentCoreGatewayInvoke",
                principal=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
                action="lambda:InvokeFunction",
                source_arn=self.gateway.attr_gateway_arn,
            )

            # The tool's JSON Schema keys (type/properties/required/description) match
            # SchemaDefinitionProperty's fields, so the raw dict passes through.
            agentcore.CfnGatewayTarget(
                self,
                f"{tool_name}Target",
                gateway_identifier=self.gateway.attr_gateway_identifier,
                name=tool_name.replace("_", "-"),
                credential_provider_configurations=[
                    agentcore.CfnGatewayTarget.CredentialProviderConfigurationProperty(
                        credential_provider_type="GATEWAY_IAM_ROLE"
                    )
                ],
                target_configuration=agentcore.CfnGatewayTarget.TargetConfigurationProperty(
                    mcp=agentcore.CfnGatewayTarget.McpTargetConfigurationProperty(
                        lambda_=agentcore.CfnGatewayTarget.McpLambdaTargetConfigurationProperty(
                            lambda_arn=fn.function_arn,
                            tool_schema=agentcore.CfnGatewayTarget.ToolSchemaProperty(
                                inline_payload=[
                                    agentcore.CfnGatewayTarget.ToolDefinitionProperty(
                                        name=schema["name"],
                                        description=schema["description"],
                                        input_schema=schema["inputSchema"],
                                    )
                                ]
                            ),
                        )
                    )
                ),
            )
