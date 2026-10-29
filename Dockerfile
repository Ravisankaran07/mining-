# Production Dockerfile for Mining Maintenance-Slot Optimiser
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and assets
COPY src/ /app/src/
COPY docs/ /app/docs/
COPY notebooks/ /app/notebooks/
COPY tests/ /app/tests/
COPY app.py /app/app.py

ENV PYTHONPATH="/app/src"
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
