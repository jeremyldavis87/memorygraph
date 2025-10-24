FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgtk-3-0 \
    libgl1-mesa-glx \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Create startup script
RUN echo '#!/bin/bash\n\
# Wait for database to be ready\n\
while ! pg_isready -h postgres -p 5432 -U memorygraph; do\n\
  echo "Waiting for database..."\n\
  sleep 2\n\
done\n\
\n\
# Run migrations\n\
alembic upgrade head\n\
\n\
# Start the application\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]