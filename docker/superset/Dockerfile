FROM apache/superset:latest

USER root

# Install system dependencies required for psycopg2 build
RUN apt-get update --allow-releaseinfo-change && \
    apt-get install -y gcc libpq-dev python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pip into Superset's venv if missing
RUN /app/.venv/bin/python -m ensurepip --upgrade

# Upgrade pip in venv
RUN /app/.venv/bin/python -m pip install --upgrade pip

# Install psycopg2 inside Superset's venv (the Python actually used by the app)
RUN /app/.venv/bin/pip install --no-cache-dir psycopg2-binary

USER superset
