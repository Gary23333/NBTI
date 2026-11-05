# Server socket
bind = "127.0.0.1:8081"
backlog = 2048

# Worker processes
# 会话存储为进程内 threading.Lock + 本地 JSON 文件（nbti/conversation.py），仅支持单 worker；
# 多 worker 必然因文件竞争丢数据。横向扩容前需先将会话存储替换为外部存储（如 Redis）。
workers = 1
worker_class = "gthread"
threads = 8

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "nbti"

# Server mechanics
# Create the app and its cleanup thread inside the worker, not before fork.
preload_app = False

