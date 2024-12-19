import os
import time
import json
from websocket import create_connection
import psutil

PROC_PATH = os.getenv("PROC_PATH", "/proc")
SYS_PATH = os.getenv("SYS_PATH", "/sys")

psutil.PROCFS_PATH = PROC_PATH

def format_system_info():
    """Fetch and format system stats from the host system."""
    uptime = time.time() - psutil.boot_time()  # System uptime in seconds

    return {
        "type": "system_info",
        "data": {
            "cpuUsage": psutil.cpu_percent(interval=1),  # CPU usage in percentage
            "memoryUsage": {
                "used": round(psutil.virtual_memory().used / (1024**3), 1),  # Used memory in GB
                "total": round(psutil.virtual_memory().total / (1024**3), 1)  # Total memory in GB
            },
            "uptime": round(uptime / 3600, 1)  # Uptime in hours
        }
    }

def send_data_to_websocket(ws_url, interval=5):
    """Send formatted system stats to the WebSocket server at regular intervals."""
    ws = None  # Initialize the ws variable
    try:
        ws = create_connection(ws_url)
        print(f"Connected to WebSocket server at {ws_url}")

        while True:
            # Fetch and format host system stats
            system_info = format_system_info()

            # Convert to JSON and send via WebSocket
            message = json.dumps(system_info)
            ws.send(message)
            print(f"Sent: {message}")

            # Wait for the next interval
            time.sleep(interval)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ws:
            ws.close()
            print("WebSocket connection closed")

if __name__ == "__main__":
    WS_URL = "ws://localhost:6672/ws"
    send_data_to_websocket(WS_URL, interval=15)
