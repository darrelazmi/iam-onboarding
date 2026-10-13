FROM python:3.11-slim

# Install system dependencies for Pandoc and WeasyPrint
RUN apt-get update && apt-get install -y \
    pandoc \
    weasyprint \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and prompts
COPY app.py prompts.py ./

# Expose port and run the API
EXPOSE 3000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
