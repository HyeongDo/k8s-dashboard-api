# Python 3.11 Alpine 이미지 사용 (가장 가벼움)
FROM python:3.11-alpine

# 작업 디렉토리 설정
WORKDIR /app

# Alpine 패키지 업데이트 및 필요한 패키지 설치
RUN apk update && apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 의존성 설치 (캐시 최적화)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 기본 환경변수 설정 (docker-compose에서 오버라이드 가능)
# Docker에서는 0.0.0.0 필요 (컨테이너 외부 접근을 위해)
ENV K8S_API=https://172.10.40.93:6443
ENV VERIFY_SSL=false
ENV DEBUG=false
ENV HOST=0.0.0.0
ENV PORT=8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행 (빠른 시작)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
