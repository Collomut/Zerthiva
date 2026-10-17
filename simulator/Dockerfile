FROM python:3.11-slim

WORKDIR /app

COPY mock_field_node.py .
COPY run_simulation.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "run_simulation.py", "--endpoint", "http://backend:8000/api/v1/ingest/telemetry", "--interval", "10"]
