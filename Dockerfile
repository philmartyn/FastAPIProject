FROM python:3.13-slim

# Keep Python output unbuffered so logs show up immediately in `docker compose logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the project and install it (deps come from pyproject.toml).
COPY . .
RUN pip install --no-cache-dir .

EXPOSE 8000

# Apply migrations, then start the API server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
