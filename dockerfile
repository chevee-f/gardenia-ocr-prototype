FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
    # PATH="$PATH:/app/poppler-24.08.0/Library/bin"

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

RUN ls -l /app && echo "Current Directory:" && pwd

RUN dpkg -l | grep poppler-utils && which pdftotext && which pdftoppm

RUN ls -l /app/poppler-24.08.0/Library/bin

# RUN /app/poppler-24.08.0/Library/bin/pdftotext -v

ENV PATH="/app/poppler-24.08.0/Library/bin:${PATH}"

RUN chmod +x /app/Tesseract-OCR/tesseract.exe
RUN ls -l /app/Tesseract-OCR/tesseract.exe

# Define the command to run your app (modify based on your entry point)
CMD ["python", "-u", "ocr-api.py"]
