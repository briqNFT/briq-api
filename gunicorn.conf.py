bind = ['0.0.0.0:5000']

# Logging
# For k8s, log to stdout/stderr
accesslog = "-"
errorlog = "-"
loglevel = "info"  # for error log
logger_class = "briq_api.logging.logging.GunicornLoggerOverride"

# Worker configuration
workers = 3
worker_class = 'briq_api.logging.uvicorn_setup.CustomLogUvicornWorker'
timeout = 60
keepalive = 5  # behind load balancer
