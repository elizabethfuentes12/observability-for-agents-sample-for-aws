"""IAM execution role for the AgentCore Runtime.

Assumed by bedrock-agentcore.amazonaws.com. Grants:
  - CloudWatch Logs write (so the runtime can emit logs / OTEL spans)
  - X-Ray write (managed policy)
  - bedrock-agentcore:* on the account's gateways/runtimes
  - bedrock:InvokeModel* for the model used by the agent
  - lambda:InvokeFunction on the tool Lambdas (name prefix travel-agent-*)
"""

from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from constructs import Construct


class AgentCoreRole(Construct):
    """The IAM role AgentCore Runtime assumes to execute the agent."""

    def __init__(self, scope: Construct, construct_id: str, *,
                 role_name: str,
                 tool_lambda_name_prefix: str = "travel-agent-",
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stack = Stack.of(self)

        self.role = iam.Role(
            self,
            "Role",
            role_name=role_name,
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            description="Execution role for the travel-agent AgentCore Runtime",
        )

        self.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
        )

        self.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
            ],
            resources=[
                f"arn:aws:logs:{stack.region}:{stack.account}:log-group:/aws/bedrock-agentcore/*",
                f"arn:aws:logs:{stack.region}:{stack.account}:log-group:/aws/bedrock-agentcore/*:*",
                f"arn:aws:logs:{stack.region}:{stack.account}:log-group:/aws/spans/*",
                f"arn:aws:logs:{stack.region}:{stack.account}:log-group:/aws/spans/*:*",
            ],
        ))

        self.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock-agentcore:*",
            ],
            resources=["*"],
        ))

        self.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
            ],
            resources=["*"],
        ))

        self.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["lambda:InvokeFunction"],
            resources=[
                f"arn:aws:lambda:{stack.region}:{stack.account}:function:{tool_lambda_name_prefix}*"
            ],
        ))
