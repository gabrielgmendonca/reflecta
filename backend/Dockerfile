FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt greenlet

# Copy application code
COPY app/ ./app/

# Create data directory for SQLite
RUN mkdir -p /data

ENV DATABASE_URL=sqlite+aiosqlite:///data/retro.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
