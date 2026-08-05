# Travel agent runtime container — ARM64, Python 3.11.
# Built by the bedrock-agentcore-starter-toolkit during `runtime.launch()`.

FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm

ENV AWS_REGION=us-east-1
ENV PYTHONUNBUFFERED=1

COPY agent_requirements.txt /app/agent_requirements.txt
RUN pip install --no-cache-dir -r /app/agent_requirements.txt \
    && pip install --no-cache-dir aws-opentelemetry-distro==0.12.2

# Non-root user required by AgentCore Runtime
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

WORKDIR /app
COPY --chown=bedrock_agentcore:bedrock_agentcore travel_agent.py /app/travel_agent.py

EXPOSE 8080

CMD ["opentelemetry-instrument", "python", "-m", "travel_agent"]
