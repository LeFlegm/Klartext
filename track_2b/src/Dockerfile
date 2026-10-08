# Stage 1: build the UI to static files (build time only, needs the npm registry)
FROM node:22-slim AS web
WORKDIR /web
COPY klartext/frontend/klartext/package*.json ./
RUN npm ci
COPY klartext/frontend/klartext/ ./
RUN npm run build

# Stage 2: the runtime image (Python only, no Node)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY klartext ./klartext
COPY --from=web /web/out ./static
EXPOSE 8000
CMD ["uvicorn", "klartext.api.main:app", "--host", "0.0.0.0", "--port", "8000"]