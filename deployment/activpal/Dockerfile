FROM python:3.12-slim

WORKDIR /app

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent pip cache
ENV PIP_NO_CACHE_DIR=1

# Install dependencies
COPY deployment/activpal/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install WEALTH package
COPY pyproject.toml .
COPY src ./src

RUN pip install --no-cache-dir .

# Copy API
COPY deployment/activpal/api.py .
COPY deployment/activpal/inference.py .

# Create directories
RUN mkdir -p /app/input /app/output

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]