FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgtk-3-0 \
    libzbar0 \
    libopengl0 \
    libgl1 \
    postgresql-client \
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
# Export library path to find OpenGL libraries\n\
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH\n\
\n\
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

# Set environment variables to force headless mode for OpenCV
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=:99.0
ENV OPENCV_IO_ENABLE_OPENEXR=0
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu

EXPOSE 8000

CMD ["/app/start.sh"]