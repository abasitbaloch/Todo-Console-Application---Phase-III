FROM python:3.11-slim

WORKDIR /app

# Copy requirements from root-relative path
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from the backend folder into the /app folder in container
COPY backend/ .

# Critical: This tells Python that the /app folder is where the 'src' module lives
ENV PYTHONPATH=/app

# Start the server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]