"""
Gunicorn configuration for Stratify AI
Production WSGI server settings
"""
import multiprocessing

# Server Socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/stratify/access.log"
errorlog = "/var/log/stratify/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = "stratify-ai"

# Server Mechanics
daemon = False
pidfile = "/var/run/stratify.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS directly via Gunicorn)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
