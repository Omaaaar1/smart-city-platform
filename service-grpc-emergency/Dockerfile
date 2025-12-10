FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Port spécifique gRPC
EXPOSE 50051

# Attention : on lance server.py ici
CMD ["python", "server.py"]