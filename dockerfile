FROM python:3.10

# Install dependencies
RUN apt update && apt install -y tesseract-ocr poppler-utils

# Set up working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Run the app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]