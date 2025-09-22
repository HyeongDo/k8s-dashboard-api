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

### 다중 클러스터 지원
- **클러스터 토큰 생성**: ID, PW, Port로 클러스터 토큰 자동 생성
- **클러스터 관리**: 여러 클러스터 설정 저장 및 관리
- **동적 클러스터 선택**: API 호출 시 클러스터 ID로 선택 가능

## 사전 요구사항

- Python 3.8+
- Kubernetes 클러스터 접근 권한
- Kubernetes API 서버 접근 가능한 네트워크

## API 사용법

### 클러스터 토큰 생성 및 저장

API는 자동으로 다음 과정을 수행합니다:

1. **ServiceAccount 생성**: `dashboard-admin` ServiceAccount를 `kubernetes-dashboard` 네임스페이스에 생성
2. **ClusterRoleBinding 생성**: `dashboard-admin` ClusterRoleBinding을 생성하여 `cluster-admin` 권한 부여
3. **토큰 발급**: Kubernetes 1.24+ 방식으로 토큰 생성

```bash
# 클러스터 토큰 생성 및 저장
curl -X POST "http://localhost:8000/clusters/token" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "your-k8s-api-server",
    "port": 6443,
    "username": "your-username",
    "password": "your-password",
    "cluster_name": "production"
  }'
```

**참고**: 
- `username`과 `password`는 클러스터에 admin 권한이 있는 사용자 계정이어야 합니다.
- API는 자동으로 `kubernetes-dashboard` 네임스페이스에 `dashboard-admin` ServiceAccount를 생성합니다.
- 생성된 토큰은 24시간 동안 유효합니다.
- 이미 존재하는 ServiceAccount나 ClusterRoleBinding이 있으면 재사용합니다.

### 클러스터 목록 조회

```bash
# 저장된 클러스터 목록 조회
curl -X GET "http://localhost:8000/clusters"
```

### 조회 API 사용 예시

```bash
# 모든 네임스페이스 조회 (기본 클러스터)
curl -X GET "http://localhost:8000/namespaces"

# 특정 클러스터의 네임스페이스 조회
curl -X GET "http://localhost:8000/namespaces?cluster_id=production"

# 특정 네임스페이스의 Pod 조회
curl -X GET "http://localhost:8000/pods/kube-system?cluster_id=production"
```

### 롤아웃 API 사용 예시

```bash
# Deployment 롤아웃
curl -X POST "http://localhost:8000/deployments/kube-system/nginx-deployment/rollout?cluster_id=production"

# DaemonSet 롤아웃
curl -X POST "http://localhost:8000/daemonsets/kube-system/fluentd/rollout?cluster_id=production"

# StatefulSet 롤아웃
curl -X POST "http://localhost:8000/statefulsets/default/mysql/rollout?cluster_id=production"
```

### 삭제 API 사용 예시

```bash
# Pod 삭제
curl -X DELETE "http://localhost:8000/pods/default/nginx-pod?cluster_id=production"
```

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

### 3. 클러스터 설정

애플리케이션 실행 후 클러스터 토큰을 생성하고 저장해야 합니다:

```bash
# 클러스터 토큰 생성 및 저장
curl -X POST "http://localhost:8000/clusters/token" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "your-k8s-api-server",
    "port": 6443,
    "username": "your-username", 
    "password": "your-password",
    "cluster_name": "production"
  }'
```

## API 엔드포인트

### 기본 엔드포인트

- `GET /`: 서버 상태 확인
- `GET /health`: 헬스 체크

### 클러스터 관리

- `POST /clusters/token`: 클러스터 토큰 생성 및 저장
- `GET /clusters`: 저장된 클러스터 목록 조회
- `GET /clusters/{cluster_id}`: 특정 클러스터 정보 조회
- `DELETE /clusters/{cluster_id}`: 클러스터 설정 삭제

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
  "message": "클러스터 'production' 토큰이 생성되고 저장되었습니다."
}
```

## 보안 고려사항

1. **토큰 보안**: 클러스터 토큰은 `config/clusters.json` 파일에 저장되므로 파일 권한을 적절히 설정하세요.
2. **네트워크 보안**: 프로덕션 환경에서는 HTTPS를 사용하고 적절한 인증을 구현하세요.
3. **권한 관리**: 최소 권한 원칙에 따라 필요한 권한만 부여하세요.

## 문제 해결

### 일반적인 문제

1. **클러스터 연결 실패**: 클러스터 API 서버 주소와 포트가 올바른지 확인하세요.
2. **토큰 생성 실패**: 사용자명과 비밀번호가 올바른지 확인하세요.
3. **권한 부족**: 토큰에 필요한 권한이 있는지 확인하세요.

## 변경 이력

### v2.0.0
- 다중 클러스터 지원 추가
- API 간소화 (조회, 삭제, 롤아웃)
- 클러스터 토큰 자동 생성 기능
- DaemonSet, StatefulSet 지원 추가

### v1.0.0
- 초기 버전
- Pod 삭제 기능
- Deployment 재시작 기능