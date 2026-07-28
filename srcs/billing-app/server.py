from app.consumer import run
from health import start_health_server

if __name__ == "__main__":
    start_health_server()
    run()
