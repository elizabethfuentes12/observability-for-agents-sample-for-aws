"""AgentCore Runtime construct — wraps CfnRuntime and uploads the agent package to S3.

Property names verified against aws-cdk-lib's aws_bedrockagentcore module:
CfnRuntime(agent_runtime_name=..., agent_runtime_artifact=..., network_configuration=...,
role_arn=...); CodeConfigurationProperty(code=CodeProperty(s3=S3LocationProperty(bucket,
prefix)), entry_point=[...], runtime=...).
"""

from aws_cdk import Stack
from aws_cdk import aws_bedrockagentcore as agentcore
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3_assets as s3_assets
from constructs import Construct


class AgentCoreRuntime(Construct):
    def __init__(self, scope: Construct, construct_id: str, *,
                 runtime_name: str,
                 agentcore_role: iam.IRole,
                 gateway_url: str,
                 model_id: str,
                 deployment_zip_path: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stack = Stack.of(self)

        package = s3_assets.Asset(self, "AgentPackage",
                                   path=deployment_zip_path)
        package.grant_read(agentcore_role)

        self.runtime = agentcore.CfnRuntime(
            self,
            "Runtime",
            agent_runtime_name=runtime_name,
            description="Travel agent — Strands + AgentCore Gateway + DynamoDB",
            agent_runtime_artifact=agentcore.CfnRuntime.AgentRuntimeArtifactProperty(
                code_configuration=agentcore.CfnRuntime.CodeConfigurationProperty(
                    code=agentcore.CfnRuntime.CodeProperty(
                        s3=agentcore.CfnRuntime.S3LocationProperty(
                            bucket=package.s3_bucket_name,
                            prefix=package.s3_object_key,
                        )
                    ),
                    entry_point=["travel_agent.py"],
                    runtime="PYTHON_3_11",
                )
            ),
            role_arn=agentcore_role.role_arn,
            network_configuration=agentcore.CfnRuntime.NetworkConfigurationProperty(
                network_mode="PUBLIC",
            ),
            environment_variables={
                "AGENTCORE_GATEWAY_URL": gateway_url,
                "BEDROCK_MODEL_ID": model_id,
                "RUNTIME_AWS_REGION": stack.region,
            },
        )
