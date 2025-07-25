import multiprocessing

# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
workers = 2  # Keep worker count low to reduce memory usage
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increase timeout to allow for OpenAI API calls
graceful_timeout = 30
keepalive = 2

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
