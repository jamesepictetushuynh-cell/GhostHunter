# Use the official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy just the requirements first to take advantage of Docker caching
RUN pip install --no-cache-dir httpx pydantic

# Copy your ultimate security script into the container
COPY ghosthunter.py .

# Run the script when the container starts
CMD ["python", "ghosthunter.py"]
