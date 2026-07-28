FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /venv && /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /var/log/api-gateway-app

EXPOSE 3000
ENTRYPOINT ["/venv/bin/python", "server.py"]
