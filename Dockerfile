FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories and make scripts executable
RUN mkdir -p data/conversations logs && chmod +x start.sh

# Expose frontend port
EXPOSE 8080

# 可选环境变量（均可不设置，保持默认单机行为）：
#   NBTI_ADMIN_TOKEN       配置写接口（POST /api/config、reset、test-connection）的管理令牌；
#                          未设置时仅本机请求视为管理员。
#   NBTI_STORAGE_BACKEND   存储后端：file（默认）或 redis。设为 redis 需镜像内安装 redis 包并
#                          提供 NBTI_REDIS_URL；否则 create_store 会自动回退文件后端。
#   NBTI_REDIS_URL         Redis 连接串（如 redis://redis:6379/0），仅 storage_backend=redis 时使用。
#   NBTI_WORKERS           gunicorn worker 数（默认 1）；>1 需先启用 Redis 存储后端。

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8081/api/health', timeout=5)" || exit 1

# Start both servers
CMD ["bash", "start.sh"]
