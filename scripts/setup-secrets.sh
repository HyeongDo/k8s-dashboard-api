#!/bin/bash

# 민감정보 설정 스크립트
echo "🔐 민감정보 설정을 시작합니다..."

# secrets 디렉토리 생성
mkdir -p secrets

# .env 파일 생성
if [ ! -f .env ]; then
    echo "📝 .env 파일을 생성합니다..."
    cp config/env.example .env
    echo "✅ .env 파일이 생성되었습니다."
    echo "⚠️  .env 파일에 실제 값을 입력해주세요."
else
    echo "ℹ️  .env 파일이 이미 존재합니다."
fi

# secrets 파일 생성
if [ ! -f secrets/secrets ]; then
    echo "🔑 secrets 파일을 생성합니다..."
    cp config/secrets.example secrets/secrets
    echo "✅ secrets 파일이 생성되었습니다."
    echo "⚠️  secrets/secrets 파일에 실제 민감정보를 입력해주세요."
else
    echo "ℹ️  secrets 파일이 이미 존재합니다."
fi

# 권한 설정
chmod 600 .env
chmod 600 secrets/secrets

echo "🔒 파일 권한이 설정되었습니다."
echo ""
echo "📋 다음 단계:"
echo "1. .env 파일에 기본 설정 입력"
echo "2. secrets/secrets 파일에 민감정보 입력"
echo "3. docker-compose up -d 실행"
