# Server socket
bind = "0.0.0.0:8080"
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
preload_app = True


def post_worker_init(worker):
    """preload_app 下 create_app 在 master 执行，守护线程不随 fork 存活，需在 worker 内重启会话清理线程"""
    from nbti.app import ensure_cleanup_thread
    ensure_cleanup_thread()
