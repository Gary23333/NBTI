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

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8081/api/health', timeout=5)" || exit 1

# Start both servers
CMD ["bash", "start.sh"]
