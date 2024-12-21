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

def send_data_to_websocket(ws):
    """Send formatted system stats to the WebSocket server at regular intervals."""
    try:
        system_info = format_system_info()
        
        message = json.dumps(system_info)
        ws.send(message)
        print(f"Sent: {message}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    WS_URL = "ws://localhost:6672/ws"
    ws = None
    
    while ws is None:
        try:
            ws = create_connection(WS_URL)
            print(f"Connected to WebSocket server at {WS_URL}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            time.sleep(5)

    try:
        while True:
            result = ws.recv()
            print(f"Received: {result}")
            data = json.loads(result)
            
            if data.get("type") == "request_system_info":
                send_data_to_websocket(ws)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ws.close()
    