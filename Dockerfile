# Use the official Python image as a base image
FROM python:3.9

# Install system dependencies including tesseract-ocr and poppler-utils
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Streamlit uses (8501)
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

