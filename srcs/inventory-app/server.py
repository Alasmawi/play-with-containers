import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("INVENTORY_APP_HOST", "0.0.0.0")
    port = int(os.environ.get("INVENTORY_APP_PORT", 8080))
    app.run(host=host, port=port)
