# --- Stage 1: Model Download ---
FROM python:3.12-slim AS builder


WORKDIR /builder

# Install required libs to download models
RUN pip install --no-cache-dir --default-timeout=100 sentence-transformers

# Set model cache path
ENV SENTENCE_TRANSFORMERS_HOME=/builder/models
RUN mkdir -p $SENTENCE_TRANSFORMERS_HOME

# Download required models
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2', cache_folder='$SENTENCE_TRANSFORMERS_HOME')"


# --- Stage 2: Final Application Image ---
    # Removed --platform, unnecessary unless cross-compiling
FROM python:3.12-slim   

WORKDIR /app

# ✅ Install bash for debugging and clean up apt cache
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy model files from builder stage
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
COPY --from=builder /builder/models $SENTENCE_TRANSFORMERS_HOME

# Copy your Python code
COPY round1b_solution.py .

# Default command
CMD ["python", "round1b_solution.py"]
