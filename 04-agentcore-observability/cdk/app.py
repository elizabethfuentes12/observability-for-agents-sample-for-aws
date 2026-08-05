"""CDK app entry point."""

import aws_cdk as cdk

from stack import TravelAgentObservabilityStack

app = cdk.App()
TravelAgentObservabilityStack(app, "TravelAgentObservabilityStack")
app.synth()
