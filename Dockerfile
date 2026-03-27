# Use a lightweight Python image
FROM python:3.12-slim

# Create a non-root user as recommended by Hugging Face
RUN useradd -m -u 1000 user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies (root required temporarily)
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    git \
    libxml2-dev \
    libxslt-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Pre-set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/data/transformers_cache
ENV HF_HOME=/app/data/hf_home
ENV NLTK_DATA=/app/data/nltk_data

# Ensure data directory and logs exist and are writable
RUN mkdir -p /app/data /app/data/logs && chmod -R 777 /app/data

USER user

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Pre-download models to avoid runtime timeout/errors
RUN python -c "import nltk; nltk.download('punkt', download_dir='/app/data/nltk_data'); nltk.download('punkt_tab', download_dir='/app/data/nltk_data')"
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/app/data/transformers_cache')"

# Copy the rest of the application
COPY --chown=user . .

# Expose the mandatory Hugging Face port
EXPOSE 7860

# Command to start the application (main:app matches our FastAPI instance)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
