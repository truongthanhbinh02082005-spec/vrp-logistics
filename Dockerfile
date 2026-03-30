# Stage 1: Build Frontend
FROM node:20 as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Final Python Image
FROM python:3.10-slim

# Set up user for Hugging Face (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

# Env vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 7860

# Install system dependencies (Switch back to root for installation)
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir whitenoise gunicorn dj-database-url

# Copy Backend code
COPY backend/ .

# Copy Frontend build to backend serving directory
COPY --from=frontend-build /app/frontend/build /app/frontend_build

# Ensure permissions for user 1000
RUN chown -R user:user /app
USER user

# Expose port (default for HF is 7860)
EXPOSE 7860

# Start via entrypoint for collective commands
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
