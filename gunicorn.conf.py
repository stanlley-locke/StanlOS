import os
import asyncio

# Ensure MainThread has a valid event loop during configuration load
try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
except Exception:
    pass

def post_fork(server, worker):
    """Ensure each worker process has a dedicated event loop before app initialization."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception:
        pass

# Server socket configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging configuration
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
errorlog = "-"
accesslog = "-"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# Process naming
proc_name = "stanlos_app"

# Server mechanics
preload_app = False
graceful_timeout = 30
