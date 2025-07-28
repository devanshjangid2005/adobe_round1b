# --- Stage 1: Model Download ---
FROM python:3.11-slim as builder

WORKDIR /builder

# Install required libs to download models
RUN pip install --no-cache-dir sentence-transformers

# Set model cache path
ENV SENTENCE_TRANSFORMERS_HOME=/builder/models
RUN mkdir -p $SENTENCE_TRANSFORMERS_HOME

# Download required models
RUN python -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('sentence-transformers/all-mpnet-base-v2', cache_folder='$SENTENCE_TRANSFORMERS_HOME'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', cache_folder='$SENTENCE_TRANSFORMERS_HOME')"

# --- Stage 2: Final Application Image ---
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# ✅ Install bash so you can debug inside container
RUN apt-get update && apt-get install -y bash

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model files from builder stage
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
COPY --from=builder /builder/models $SENTENCE_TRANSFORMERS_HOME

# Copy your Python code
COPY round1b_solution.py .

# Default command
CMD ["python", "round1b_solution.py"]
