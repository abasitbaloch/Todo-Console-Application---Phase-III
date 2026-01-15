# 1. Use an official Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies for PostgreSQL (needed for asyncpg/psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file and install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your backend code (src, alembic, etc.)
COPY . .

# 6. Expose the port Hugging Face uses
EXPOSE 7860

# 7. Start the FastAPI application using Uvicorn
# Note: We use 0.0.0.0 and port 7860 for Hugging Face compatibility
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]