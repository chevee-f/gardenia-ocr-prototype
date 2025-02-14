FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="$PATH:/opt/render/project/src/poppler-24.08.0/Library/bin"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose port (if using a web API)
EXPOSE 5000

# Define the command to run your app (modify based on your entry point)
CMD ["python", "ocr-api.py"]
