#!/bin/bash

# Render 배포용 시작 스크립트

echo "Starting 재고마스터 application..."

# Streamlit 앱 실행
streamlit run app/main.py --server.port=${PORT:-8501} --server.address=0.0.0.0
