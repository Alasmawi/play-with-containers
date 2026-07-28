import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("GATEWAY_APP_HOST", "0.0.0.0")
    port = int(os.environ.get("GATEWAY_APP_PORT", 3000))
    app.run(host=host, port=port)
