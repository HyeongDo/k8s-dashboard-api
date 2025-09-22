# Kubernetes 토큰 설정 가이드

## 🚨 중요: 토큰 생성이 아닌 토큰 설정

이 API는 **토큰을 생성하는 것이 아니라 기존 토큰을 설정**하는 것입니다. 
Kubernetes 클러스터에 접근하려면 **이미 존재하는 유효한 토큰**이 필요합니다.

## 📋 토큰 획득 방법

### 방법 1: kubectl을 사용하여 토큰 생성 (권장)

```bash
# 1. ServiceAccount 생성
kubectl create serviceaccount dashboard-admin -n kubernetes-dashboard

# 2. ClusterRoleBinding 생성
kubectl create clusterrolebinding dashboard-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=kubernetes-dashboard:dashboard-admin

# 3. 토큰 생성 (Kubernetes 1.24+)
kubectl create token dashboard-admin -n kubernetes-dashboard --duration=24h
```

### 방법 2: 기존 ServiceAccount의 토큰 사용

```bash
# 기존 ServiceAccount 목록 확인
kubectl get serviceaccounts -A

# 특정 ServiceAccount의 토큰 생성
kubectl create token <serviceaccount-name> -n <namespace> --duration=24h
```

### 방법 3: kubeconfig에서 토큰 추출

```bash
# kubeconfig 파일에서 토큰 확인
kubectl config view --raw -o jsonpath='{.users[0].user.token}'
```

## 🔧 API 사용 방법

### 1. SSH를 통한 자동 토큰 생성 (권장) ⭐

클러스터 VM에 SSH로 접속하여 자동으로 토큰을 생성합니다:

```bash
curl -X POST "http://localhost:8000/clusters/ssh-token" \
     -H "Content-Type: application/json" \
     -d '{
       "ssh_host": "172.20.10.94",
       "ssh_port": 22,
       "ssh_username": "your-ssh-username",
       "ssh_password": "your-ssh-password",
       "k8s_host": "172.20.10.94",
       "k8s_port": 6443,
       "cluster_name": "default",
       "service_account": "dashboard-admin",
       "namespace": "kubernetes-dashboard",
       "verify_ssl": false
     }'
```

**이 방법의 장점:**
- 클러스터 관리자 권한이 필요 없음
- SSH 접근 권한만 있으면 됨
- 자동으로 ServiceAccount와 ClusterRoleBinding 생성
- 토큰 유효성 자동 검증

### 2. 기존 토큰으로 설정

```bash
curl -X POST "http://localhost:8000/clusters/token" \
     -H "Content-Type: application/json" \
     -d '{
       "host": "172.20.10.94",
       "port": 6443,
       "cluster_name": "default",
       "existing_token": "your-actual-kubernetes-token-here"
     }'
```

### 3. Basic Auth 사용 (클러스터에서 지원하는 경우)

```bash
curl -X POST "http://localhost:8000/clusters/token" \
     -H "Content-Type: application/json" \
     -d '{
       "host": "172.20.10.94",
       "port": 6443,
       "cluster_name": "default",
       "username": "your-username",
       "password": "your-password"
     }'
```

### 4. 직접 토큰 설정

```bash
curl -X POST "http://localhost:8000/clusters/set-token" \
     -H "Content-Type: application/json" \
     -d '{
       "cluster_id": "default",
       "token": "your-actual-kubernetes-token-here",
       "host": "172.20.10.94",
       "port": 6443,
       "verify_ssl": false
     }'
```

## 🧪 테스트 방법

토큰 설정 후 다음 명령어로 테스트:

```bash
# 1. 서버 실행
python main.py

# 2. 클러스터 목록 확인
curl http://localhost:8000/clusters

# 3. 네임스페이스 목록 조회 (토큰 테스트)
curl http://localhost:8000/namespaces

# 4. 전체 테스트 실행
python test_local.py
```

## ⚠️ 주의사항

1. **포트 번호**: Kubernetes API는 보통 6443 포트를 사용합니다 (22번 포트 아님)
2. **토큰 유효성**: 토큰은 클러스터 관리자 권한이 있어야 생성할 수 있습니다
3. **SSL 인증서**: 개발 환경에서는 `verify_ssl: false`를 사용할 수 있습니다
4. **토큰 만료**: 생성된 토큰은 시간이 지나면 만료됩니다

## 🔍 문제 해결

### "system:anonymous" 오류
- 이는 권한이 없는 사용자로 토큰을 생성하려고 할 때 발생합니다
- **해결책**: 클러스터 관리자 권한으로 토큰을 미리 생성하세요

### "SSL: WRONG_VERSION_NUMBER" 오류
- 잘못된 포트 번호를 사용했을 때 발생합니다
- **해결책**: 포트 6443을 사용하세요 (22번 포트 아님)

### "토큰이 유효하지 않습니다" 오류
- 만료되었거나 잘못된 토큰을 사용했을 때 발생합니다
- **해결책**: 새로운 토큰을 생성하세요
