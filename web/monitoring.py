# shayan.txt
"""Monitoring endpoints."""

import time
import psutil
from pathlib import Path

start_time = time.time()

def get_stats():
    uptime = time.time() - start_time
    cpu = psutil.cpu_percent(interval=0.5) if psutil else 0
    mem = psutil.virtual_memory().percent if psutil else 0
    return {
        "uptime_seconds": int(uptime),
        "cpu_percent": cpu,
        "memory_percent": mem,
    }
