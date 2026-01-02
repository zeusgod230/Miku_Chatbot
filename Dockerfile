# Use a lightweight official Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure stdout/stderr are not buffered (better logs)
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies (optional but safe)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better Docker cache)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Create logs directory if not present
RUN mkdir -p logs

# Expose nothing (Telegram bots don't need ports)
# EXPOSE 8000  ❌ not needed

# Run the bot
CMD ["python", "main.py"]

