FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    portaudio19-dev \
    libsndfile1 \
    python3-tk \
    tk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN mkdir -p data

CMD ["python", "main.py"]