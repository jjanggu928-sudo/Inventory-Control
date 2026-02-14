FROM python:3.13-slim

WORKDIR /app

# 시스템 패키지 설치 (zxing-cpp 빌드용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/healthz || exit 1

ENTRYPOINT ["streamlit", "run", "main.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
