import os

# Server socket configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
# Render recommends 2 workers per instance for optimal memory and async performance
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
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
