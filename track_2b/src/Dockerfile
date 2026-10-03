FROM python:3.12-slim

# Working directory inside the container (Linux path)
WORKDIR /app

# Copy only the dependency list first, so these layers stay cached when code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the whole package (including __init__.py files)
COPY klartext ./klartext

EXPOSE 8000

# Exec form: uvicorn runs as the main process and receives stop signals directly
CMD ["uvicorn", "klartext.api.main:app", "--host", "0.0.0.0", "--port", "8000"]