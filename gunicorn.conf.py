import multiprocessing
import os

# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html

# Server socket - use PORT environment variable if set (required for Render)
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Worker processes - use minimal workers to save memory
workers = int(os.environ.get("WEB_CONCURRENCY", 1))
worker_class = "sync"
worker_connections = 500
timeout = 150  # Longer timeout to allow for OpenAI API calls
graceful_timeout = 30
keepalive = 2

# Reduce memory usage
max_requests = 500
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "saas-shop"

# Server mechanics
preload_app = True  # Preload application code before forking

# Debugging
reload = False
spew = False

# Server hooks
def on_starting(server):
    print("Starting gunicorn with memory-optimized settings")

def post_fork(server, worker):
    print(f"Worker spawned (pid: {worker.pid})")

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
