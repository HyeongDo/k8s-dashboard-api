# Kubernetes Dashboard API

쿠버네티스 클러스터 관리를 위한 커스텀 REST API 서버입니다. Pod 삭제와 Deployment 재시작 기능을 제공합니다.

## 기능

- **Pod 삭제**: 특정 네임스페이스의 Pod를 안전하게 삭제
- **Deployment 재시작**: 특정 네임스페이스의 Deployment를 재시작하여 롤아웃 트리거

## 사전 요구사항

- Python 3.8+
- Kubernetes 클러스터 접근 권한
- Kubernetes API 서버 토큰

## 설치 및 실행

### 1. 가상환경 설정

#### Windows 11
```cmd
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

#### Linux/macOS
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Kubernetes 토큰 발급

#### Kubernetes Dashboard 토큰 발급
```bash
# admin-user 토큰 생성
kubectl -n kubernetes-dashboard create token admin-user > token.txt

# 토큰을 환경변수로 설정
export K8S_TOKEN=$(cat token.txt)
```

#### Service Account 토큰 발급 (대안)
```bash
# Service Account 생성
kubectl create serviceaccount k8s-dashboard-api

# ClusterRoleBinding 생성 (필요한 권한에 따라 조정)
kubectl create clusterrolebinding k8s-dashboard-api-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=default:k8s-dashboard-api

# 토큰 발급
kubectl create token k8s-dashboard-api > token.txt
export K8S_TOKEN=$(cat token.txt)
```

### 3. 환경변수 설정

#### Windows 11
```cmd
set K8S_TOKEN=your-kubernetes-token
```

#### Linux/macOS
```bash
export K8S_TOKEN="your-kubernetes-token"
```

### 4. 서버 실행
```bash
# 로컬 개발 (보안상 localhost만 접근 가능)
uvicorn main:app --host 127.0.0.1 --port 8000

# 또는 환경변수로 설정
export HOST=127.0.0.1
uvicorn main:app --host $HOST --port 8000
```

## API 사용법

### 기본 엔드포인트
- `GET /` - API 정보
- `GET /health` - 헬스체크

### Namespace 관리
```bash
# 모든 네임스페이스 조회
curl -X GET http://localhost:8000/namespaces

# 특정 네임스페이스 조회
curl -X GET http://localhost:8000/namespaces/{namespace}
```

### Pod 관리
```bash
# 모든 Pod 조회
curl -X GET http://localhost:8000/pods

# 특정 네임스페이스의 Pod 조회
curl -X GET http://localhost:8000/pods/{namespace}

# 특정 Pod 조회
curl -X GET http://localhost:8000/pods/{namespace}/{pod-name}

# Pod 삭제
curl -X DELETE http://localhost:8000/pods/{namespace}/{pod-name}
```

### Deployment 관리
```bash
# 모든 Deployment 조회
curl -X GET http://localhost:8000/deployments

# 특정 네임스페이스의 Deployment 조회
curl -X GET http://localhost:8000/deployments/{namespace}

# 특정 Deployment 조회
curl -X GET http://localhost:8000/deployments/{namespace}/{deployment-name}

# Deployment 재시작
curl -X POST http://localhost:8000/deployments/{namespace}/{deployment-name}/restart
```

### Service 관리
```bash
# 모든 Service 조회
curl -X GET http://localhost:8000/services

# 특정 네임스페이스의 Service 조회
curl -X GET http://localhost:8000/services/{namespace}
```

### Node 관리
```bash
# 모든 Node 조회
curl -X GET http://localhost:8000/nodes

# 특정 Node 조회
curl -X GET http://localhost:8000/nodes/{node-name}
```

## 설정

- `K8S_API`: Kubernetes API 서버 URL (기본값: `https://172.10.40.93:6443`)
- `K8S_TOKEN`: Kubernetes 인증 토큰 (환경변수로 설정)
- `VERIFY_SSL`: SSL 인증서 검증 여부 (기본값: `False`)

## 보안 주의사항

- Kubernetes 토큰은 환경변수로 관리하세요
- 프로덕션 환경에서는 SSL 인증서 검증을 활성화하세요
- 적절한 RBAC 권한을 설정하여 최소 권한 원칙을 따르세요
- **네트워크 보안**: 
  - 로컬 개발: `HOST=127.0.0.1` (localhost만 접근 가능)
  - Docker: `HOST=0.0.0.0` (컨테이너 외부 접근을 위해 필요)
  - 프로덕션: 방화벽과 리버스 프록시 사용 권장

## Docker 사용법

### Docker로 실행
```bash
# 이미지 빌드
docker build -t k8s-dashboard-api .

# 컨테이너 실행
docker run -p 8000:8000 -e K8S_TOKEN=your-token k8s-dashboard-api
```

### Docker Compose로 실행
```bash
# 1. 환경변수 설정
export K8S_TOKEN="your-kubernetes-token"

# 2. 설정 파일 복사 (선택사항)
cp config/env.example .env

# 3. 서비스 시작
docker-compose up -d

# 4. 서비스 중지
docker-compose down
```

### 환경변수 파일 사용
```bash
# .env 파일 생성
cat > .env << EOF
K8S_API=https://172.10.40.93:6443
K8S_TOKEN=your-kubernetes-token-here
VERIFY_SSL=false
DEBUG=false
HOST=0.0.0.0
PORT=8000
EOF

# Docker Compose 실행
docker-compose up -d
```

## GitHub Actions CI/CD

이 프로젝트는 GitHub Actions를 사용하여 자동화된 CI/CD 파이프라인을 제공합니다:

- **테스트**: 코드 품질 검사 및 테스트 실행
- **Docker 빌드**: 멀티 아키텍처 Docker 이미지 빌드
- **자동 배포**: main 브랜치에 푸시 시 자동 배포

### CI 사용법

#### 1. GitHub 저장소 설정
```bash
# GitHub에 저장소 생성 후 코드 푸시
git remote add origin https://github.com/brighr93/k8s-dashboard-api.git
git push -u origin main
```

#### 2. GitHub Container Registry 권한 설정
1. GitHub 저장소 → Settings → Actions → General
2. "Workflow permissions" → "Read and write permissions" 선택
3. "Allow GitHub Actions to create and approve pull requests" 체크

#### 3. 자동 빌드 트리거
- **main 브랜치에 푸시**: 자동으로 테스트, 빌드, 배포 실행
- **develop 브랜치에 푸시**: 테스트만 실행
- **Pull Request**: 테스트 실행

#### 4. 수동 빌드 실행
```bash
# 특정 태그로 빌드
git tag v1.0.0
git push origin v1.0.0
```

### GitHub Container Registry

빌드된 이미지는 GitHub Container Registry에서 확인할 수 있습니다:
```
ghcr.io/brighr93/k8s-dashboard-api:latest
ghcr.io/brighr93/k8s-dashboard-api:main
ghcr.io/brighr93/k8s-dashboard-api:v1.0.0
```

### 로컬에서 Docker 이미지 사용
```bash
# GitHub Container Registry에서 이미지 가져오기
docker pull ghcr.io/brighr93/k8s-dashboard-api:latest

# 이미지 실행
docker run -p 8000:8000 -e K8S_TOKEN=your-token ghcr.io/brighr93/k8s-dashboard-api:latest
```

## 테스트

```bash
# 테스트 실행
pytest

# 커버리지와 함께 테스트 실행
pytest --cov=app --cov-report=html
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

