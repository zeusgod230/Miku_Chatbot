FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot.py .

# Create directory for logs and data
RUN mkdir -p /app/logs /app/data

EXPOSE 8080

# Set environment variables (override these when running)
ENV TELEGRAM_TOKEN="" \
    GEMINI_API_KEY="" \
    OWNER_USER_ID="" \
    PORT=8080 \
    PYTHONUNBUFFERED=1

# Health check (Docker will mark container as healthy)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost', 8080); conn.request('GET', '/health'); response = conn.getresponse(); exit(0 if response.status == 200 else 1)"

# Run the bot
CMD ["python", "-u", "bot.py"]
