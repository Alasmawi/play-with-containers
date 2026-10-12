FROM debian:bookworm-slim

# Identical in all three app images, so this layer is built once and shared.
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-venv && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --system --no-create-home app

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
# Dependencies before source: code edits don't invalidate the pip layer.
COPY requirements.txt .
RUN python3 -m venv /venv && /venv/bin/pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /var/log/api-gateway-app && chown app:app /var/log/api-gateway-app

COPY . .

USER app
EXPOSE 3000
ENTRYPOINT ["/venv/bin/python", "server.py"]
