FROM apache/airflow:3.0.0

# User the root user
USER root

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container
COPY cfg /app/cfg
COPY data /app/data
COPY src /app/src
COPY main.py /app/main.py
COPY readme.md /app/readme.md
# COPY .python-version /app/.python-version
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Install the application dependencies
WORKDIR /app
ENV UV_SYSTEM_PYTHON=1
RUN uv pip install --system .
