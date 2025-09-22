# Kubernetes Dashboard API v2.0

쿠버네티스 클러스터 관리를 위한 커스텀 REST API 서버입니다. 다중 클러스터 지원과 간소화된 API를 제공합니다.

## 주요 기능

### 조회 API
- **Namespace**: 모든 네임스페이스 및 특정 네임스페이스 조회
- **Pod**: 모든 Pod, 네임스페이스별 Pod, 특정 Pod 조회
- **Deployment**: 모든 Deployment, 네임스페이스별 Deployment, 특정 Deployment 조회
- **DaemonSet**: 모든 DaemonSet, 네임스페이스별 DaemonSet, 특정 DaemonSet 조회
- **StatefulSet**: 모든 StatefulSet, 네임스페이스별 StatefulSet, 특정 StatefulSet 조회

### 삭제 API
- **Pod 삭제**: 특정 네임스페이스의 Pod를 안전하게 삭제

### 롤아웃 API
- **Deployment 롤아웃**: Deployment 재시작 및 상태 모니터링
- **DaemonSet 롤아웃**: DaemonSet 재시작 및 상태 모니터링
- **StatefulSet 롤아웃**: StatefulSet 재시작 및 상태 모니터링

### 클러스터 관리
- **SSH 토큰 생성**: SSH를 통해 클러스터 VM에 접속하여 토큰 자동 생성
- **토큰 직접 설정**: 기존 토큰을 직접 설정
- **동적 기본 클러스터**: 가장 최근 설정된 클러스터를 기본으로 사용
- **다중 클러스터 지원**: 여러 클러스터 설정 저장 및 관리

## 사전 요구사항

- Python 3.8+
- Kubernetes 클러스터 접근 권한
- SSH 접근 권한 (토큰 생성 시)
- Kubernetes API 서버 접근 가능한 네트워크

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

### 2. 애플리케이션 실행

#### Windows 11
```cmd
# 서버 실행
python main.py
```

#### Linux/macOS
```bash
# 서버 실행
python3 main.py
```

서버가 실행되면 `http://localhost:8000`에서 API에 접근할 수 있습니다.

## API 사용법

### 1. SSH를 통한 클러스터 토큰 생성

SSH를 통해 클러스터 VM에 접속하여 토큰을 자동 생성합니다:

```bash
curl -X POST "http://localhost:8000/clusters/ssh-token" \
  -H "Content-Type: application/json" \
  -d '{
    "ssh_host": "192.168.1.100",
    "ssh_port": 22,
    "ssh_username": "ubuntu",
    "ssh_password": "your_password",
    "k8s_host": "192.168.1.100",
    "k8s_port": 6443,
    "cluster_name": "production"
  }'
```

**자동 생성 과정:**
1. SSH로 클러스터 VM에 접속
2. `dashboard-admin` ServiceAccount를 `default` 네임스페이스에 생성
3. `dashboard-admin` ClusterRoleBinding을 생성하여 `cluster-admin` 권한 부여
4. 영구 유효한 JWT 토큰 생성
5. 토큰 유효성 검증 후 `clusters.json`에 저장

### 2. 기존 토큰 직접 설정

이미 가지고 있는 유효한 토큰을 직접 설정합니다:

```bash
curl -X POST "http://localhost:8000/clusters/set-token" \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_id": "production",
    "token": "eyJhbGciOiJSUzI1NiIs...",
    "host": "192.168.1.100",
    "port": 6443,
    "verify_ssl": false
  }'
```

### 3. 클러스터 목록 조회

```bash
# 저장된 클러스터 목록 조회
curl -X GET "http://localhost:8000/clusters"

# 특정 클러스터 정보 조회
curl -X GET "http://localhost:8000/clusters/production"
```

### 4. 조회 API 사용 예시

```bash
# 기본 클러스터로 조회 (가장 최근 설정된 클러스터)
curl -X GET "http://localhost:8000/namespaces"

# 특정 클러스터로 조회
curl -X GET "http://localhost:8000/namespaces?cluster_id=production"

# 특정 네임스페이스의 Pod 조회
curl -X GET "http://localhost:8000/pods/kube-system?cluster_id=production"
```

### 5. 롤아웃 API 사용 예시

```bash
# Deployment 롤아웃
curl -X POST "http://localhost:8000/deployments/kube-system/nginx-deployment/rollout?cluster_id=production"

# DaemonSet 롤아웃
curl -X POST "http://localhost:8000/daemonsets/kube-system/fluentd/rollout?cluster_id=production"

# StatefulSet 롤아웃
curl -X POST "http://localhost:8000/statefulsets/default/mysql/rollout?cluster_id=production"
```

### 6. 삭제 API 사용 예시

```bash
# Pod 삭제
curl -X DELETE "http://localhost:8000/pods/default/nginx-pod?cluster_id=production"
```

## API 엔드포인트

### 기본 엔드포인트

- `GET /`: 서버 상태 확인
- `GET /health`: 헬스 체크

### 클러스터 관리

- `POST /clusters/ssh-token`: SSH를 통한 클러스터 토큰 생성 및 저장
- `POST /clusters/set-token`: 기존 토큰 직접 설정
- `GET /clusters`: 저장된 클러스터 목록 조회
- `GET /clusters/{cluster_id}`: 특정 클러스터 정보 조회

### 조회 API

#### Namespace
- `GET /namespaces?cluster_id={cluster_id}`: 모든 네임스페이스 조회
- `GET /namespaces/{namespace}?cluster_id={cluster_id}`: 특정 네임스페이스 조회

#### Pod
- `GET /pods?cluster_id={cluster_id}`: 모든 Pod 조회
- `GET /pods/{namespace}?cluster_id={cluster_id}`: 특정 네임스페이스의 Pod 조회
- `GET /pods/{namespace}/{pod}?cluster_id={cluster_id}`: 특정 Pod 조회

#### Deployment
- `GET /deployments?cluster_id={cluster_id}`: 모든 Deployment 조회
- `GET /deployments/{namespace}?cluster_id={cluster_id}`: 특정 네임스페이스의 Deployment 조회
- `GET /deployments/{namespace}/{deployment}?cluster_id={cluster_id}`: 특정 Deployment 조회

#### DaemonSet
- `GET /daemonsets?cluster_id={cluster_id}`: 모든 DaemonSet 조회
- `GET /daemonsets/{namespace}?cluster_id={cluster_id}`: 특정 네임스페이스의 DaemonSet 조회
- `GET /daemonsets/{namespace}/{daemonset}?cluster_id={cluster_id}`: 특정 DaemonSet 조회

#### StatefulSet
- `GET /statefulsets?cluster_id={cluster_id}`: 모든 StatefulSet 조회
- `GET /statefulsets/{namespace}?cluster_id={cluster_id}`: 특정 네임스페이스의 StatefulSet 조회
- `GET /statefulsets/{namespace}/{statefulset}?cluster_id={cluster_id}`: 특정 StatefulSet 조회

### 삭제 API

#### Pod
- `DELETE /pods/{namespace}/{pod}?cluster_id={cluster_id}`: Pod 삭제

### 롤아웃 API

#### Deployment
- `POST /deployments/{namespace}/{deployment}/rollout?cluster_id={cluster_id}&timeout={seconds}`: Deployment 롤아웃

#### DaemonSet
- `POST /daemonsets/{namespace}/{daemonset}/rollout?cluster_id={cluster_id}&timeout={seconds}`: DaemonSet 롤아웃

#### StatefulSet
- `POST /statefulsets/{namespace}/{statefulset}/rollout?cluster_id={cluster_id}&timeout={seconds}`: StatefulSet 롤아웃

## 응답 형식

### 성공 응답
```json
{
  "status": 200,
  "response": {
    "apiVersion": "v1",
    "kind": "PodList",
    "items": [...]
  }
}
```

### 롤아웃 성공 응답
```json
{
  "status": "success",
  "message": "Deployment Rollout 완료",
  "replicas": {
    "spec": 3,
    "ready": 3,
    "available": 3
  },
  "duration": 15.2
}
```

### 클러스터 토큰 생성 성공 응답
```json
{
  "status": "success",
  "message": "SSH를 통해 클러스터 'production' 토큰이 생성되고 저장되었습니다.",
  "ssh_host": "192.168.1.100",
  "k8s_host": "192.168.1.100"
}
```

## 동적 기본 클러스터

API는 가장 최근에 설정된 클러스터를 기본값으로 사용합니다:

- `cluster_id` 파라미터를 지정하지 않으면 자동으로 마지막에 설정된 클러스터 사용
- 명시적으로 `cluster_id`를 지정하면 해당 클러스터 사용
- 클러스터 설정 순서에 따라 기본 클러스터가 동적으로 변경됨

## 보안 고려사항

1. **토큰 보안**: 클러스터 토큰은 `config/clusters.json` 파일에 저장되므로 파일 권한을 적절히 설정하세요.
2. **네트워크 보안**: 프로덕션 환경에서는 HTTPS를 사용하고 적절한 인증을 구현하세요.
3. **SSH 보안**: SSH 접근 시 강력한 비밀번호나 SSH 키를 사용하세요.
4. **권한 관리**: 최소 권한 원칙에 따라 필요한 권한만 부여하세요.

## 문제 해결

### 일반적인 문제

1. **클러스터 연결 실패**: 클러스터 API 서버 주소와 포트가 올바른지 확인하세요.
2. **SSH 연결 실패**: SSH 호스트, 포트, 사용자명, 비밀번호가 올바른지 확인하세요.
3. **토큰 생성 실패**: 클러스터에 kubectl이 설치되어 있고 권한이 있는지 확인하세요.
4. **권한 부족**: 토큰에 필요한 권한이 있는지 확인하세요.

## Docker 지원

### Docker로 실행

```bash
# 이미지 빌드
docker build -t k8s-dashboard-api .

# 컨테이너 실행
docker run -p 8000:8000 k8s-dashboard-api
```

### Docker Compose로 실행

```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down
```

## 변경 이력

### v2.0.0
- SSH를 통한 클러스터 토큰 자동 생성 기능 추가
- 기존 토큰 직접 설정 기능 추가
- 동적 기본 클러스터 지원
- 다중 클러스터 지원
- API 간소화 (조회, 삭제, 롤아웃)
- DaemonSet, StatefulSet 지원 추가
- Docker 지원 추가

### v1.0.0
- 초기 버전
- Pod 삭제 기능
- Deployment 재시작 기능