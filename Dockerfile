FROM python:3.10-slim

WORKDIR /app

# Install system utilities (optional but recommended for health checks and debugging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (ignoring errors if there are windows-specific packages like pywin32, though the slim image handles most pure python well)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the Flask port
EXPOSE 7000

# Set an environment variable so the app knows it's inside docker 
ENV RUNNING_IN_DOCKER=true

# Start the Flask app
CMD ["python", "agentic_medicore_enhanced.py"]
