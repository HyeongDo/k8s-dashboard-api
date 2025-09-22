# 로컬 테스트 가이드

## 1. 서버 실행

### 방법 1: Python으로 직접 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

### 방법 2: uvicorn으로 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# uvicorn으로 실행
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## 2. 서버 확인

서버가 실행되면 다음 URL에서 확인할 수 있습니다:

- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health

## 3. 자동 테스트 실행

```bash
# 테스트 스크립트 실행
python test_local.py
```

## 4. 수동 테스트

### 4.1 기본 엔드포인트 테스트

```bash
# 서버 상태 확인
curl http://localhost:8000/

# 헬스 체크
curl http://localhost:8000/health

# 클러스터 목록 조회
curl http://localhost:8000/clusters
```

### 4.2 클러스터 토큰 생성 테스트

```bash
# 클러스터 토큰 생성 (실제 클러스터 정보 필요)
curl -X POST "http://localhost:8000/clusters/token" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "your-k8s-api-server",
    "port": 6443,
    "username": "your-username",
    "password": "your-password",
    "cluster_name": "test-cluster"
  }'
```

### 4.3 API 문서 확인

브라우저에서 http://localhost:8000/docs 접속하여 Swagger UI로 API를 테스트할 수 있습니다.

## 5. 예상 결과

### 성공적인 서버 실행
```
서버 시작: http://127.0.0.1:8000
API 문서: http://127.0.0.1:8000/docs
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 성공적인 테스트 실행
```
Kubernetes Dashboard API 로컬 테스트 시작
==================================================

=== 서버 헬스 체크 ===
상태 코드: 200
응답: {'status': 'healthy', 'timestamp': '2024-01-01T12:00:00.000000'}

✅ 서버가 실행 중입니다.

==================== 루트 엔드포인트 ====================
상태 코드: 200
응답: {'message': 'Kubernetes Dashboard API', 'version': '2.0.0'}
✅ 루트 엔드포인트 통과

==================== 클러스터 목록 조회 ====================
상태 코드: 200
응답: []
✅ 클러스터 목록 조회 통과

==================== API 문서 접근 ====================
상태 코드: 200
API 문서에 성공적으로 접근했습니다.
문서 URL: http://localhost:8000/docs
✅ API 문서 접근 통과

==================================================
테스트 결과: 4/4 통과
🎉 모든 테스트가 통과했습니다!

API 문서: http://localhost:8000/docs
서버 중지: Ctrl+C
```

## 6. 문제 해결

### 서버가 시작되지 않는 경우
1. 포트 8000이 이미 사용 중인지 확인
2. Python 버전이 3.8 이상인지 확인
3. 의존성 패키지가 모두 설치되었는지 확인

### 테스트가 실패하는 경우
1. 서버가 실행 중인지 확인
2. 방화벽 설정 확인
3. 네트워크 연결 상태 확인

## 7. 다음 단계

로컬 테스트가 성공하면:

1. **실제 클러스터 연결 테스트**: 유효한 Kubernetes 클러스터 정보로 토큰 생성 테스트
2. **API 기능 테스트**: 생성된 토큰으로 실제 Kubernetes 리소스 조회/관리 테스트
3. **프로덕션 배포**: Docker 또는 다른 배포 방식으로 프로덕션 환경에 배포

