from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
from typing import List, Optional
from config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="쿠버네티스 클러스터 관리를 위한 REST API",
    version=settings.APP_VERSION
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Namespace 관련 API
@app.get("/namespaces")
def get_namespaces():
    """모든 네임스페이스 조회"""
    url = f"{settings.K8S_API}/api/v1/namespaces"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/namespaces/{namespace}")
def get_namespace(namespace: str):
    """특정 네임스페이스 조회"""
    url = f"{settings.K8S_API}/api/v1/namespaces/{namespace}"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

# Pod 관련 API
@app.get("/pods")
def get_all_pods():
    """모든 Pod 조회"""
    url = f"{settings.K8S_API}/api/v1/pods"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/pods/{namespace}")
def get_pods_in_namespace(namespace: str):
    """특정 네임스페이스의 Pod 조회"""
    url = f"{settings.K8S_API}/api/v1/namespaces/{namespace}/pods"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/pods/{namespace}/{pod}")
def get_pod(namespace: str, pod: str):
    """특정 Pod 조회"""
    url = f"{settings.K8S_API}/api/v1/namespaces/{namespace}/pods/{pod}"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.delete("/pods/{namespace}/{pod}")
def delete_pod(namespace: str, pod: str):
    """Pod 삭제 (권장하지 않음 - rollout 사용 권장)"""
    url = f"{settings.K8S_API}/api/v1/namespaces/{namespace}/pods/{pod}"
    r = requests.delete(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    return {"status": r.status_code, "response": r.json()}

# Deployment 관련 API
@app.get("/deployments")
def get_all_deployments():
    """모든 Deployment 조회"""
    url = f"{settings.K8S_API}/apis/apps/v1/deployments"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/deployments/{namespace}")
def get_deployments_in_namespace(namespace: str):
    """특정 네임스페이스의 Deployment 조회"""
    url = f"{settings.K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/deployments/{namespace}/{deployment}")
def get_deployment(namespace: str, deployment: str):
    """특정 Deployment 조회"""
    url = f"{settings.K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.post("/deployments/{namespace}/{deployment}/restart")
def rollout_restart(namespace: str, deployment: str):
    """Deployment 재시작 (즉시 반환)"""
    url = f"{settings.K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
    patch = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "kubectl.kubernetes.io/restartedAt": datetime.utcnow().isoformat()
                    }
                }
            }
        }
    }
    r = requests.patch(url, headers={**settings.headers, "Content-Type": "application/merge-patch+json"},
                       json=patch, verify=settings.VERIFY_SSL)
    return {"status": r.status_code, "response": r.json()}

@app.post("/deployments/{namespace}/{deployment}/rollout")
def rollout_with_monitoring(namespace: str, deployment: str, timeout: int = 30):
    """Deployment 재시작 및 상태 모니터링"""
    import time
    
    # 1. Deployment 재시작 요청
    url = f"{settings.K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
    patch = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "kubectl.kubernetes.io/restartedAt": datetime.utcnow().isoformat()
                    }
                }
            }
        }
    }
    
    # 재시작 요청
    r = requests.patch(url, headers={**settings.headers, "Content-Type": "application/merge-patch+json"},
                       json=patch, verify=settings.VERIFY_SSL)
    
    if r.status_code != 200:
        return {"status": "error", "message": "Rollout 요청 실패", "details": r.json()}
    
    # 2. 상태 모니터링
    start_time = time.time()
    check_interval = 1  # 1초마다 체크
    
    while time.time() - start_time < timeout:
        # Deployment 상태 확인
        status_url = f"{settings.K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
        status_r = requests.get(status_url, headers=settings.headers, verify=settings.VERIFY_SSL)
        
        if status_r.status_code == 200:
            deployment_data = status_r.json()
            spec_replicas = deployment_data.get('spec', {}).get('replicas', 0)
            ready_replicas = deployment_data.get('status', {}).get('readyReplicas', 0)
            available_replicas = deployment_data.get('status', {}).get('availableReplicas', 0)
            
            # 모든 조건이 만족되면 성공
            if (ready_replicas == spec_replicas and 
                available_replicas == spec_replicas and 
                spec_replicas > 0):
                return {
                    "status": "success",
                    "message": "Rollout 완료",
                    "replicas": {
                        "spec": spec_replicas,
                        "ready": ready_replicas,
                        "available": available_replicas
                    },
                    "duration": round(time.time() - start_time, 2)
                }
        
        time.sleep(check_interval)
    
    # 타임아웃
    return {
        "status": "timeout",
        "message": f"Rollout이 {timeout}초 내에 완료되지 않았습니다",
        "duration": timeout
    }

@app.get("/deployments/{namespace}/{deployment}/status")
def get_deployment_status(namespace: str, deployment: str):
    """Deployment 상태 조회"""
    url = f"{settings.K8S_API}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    
    deployment_data = r.json()
    spec = deployment_data.get('spec', {})
    status = deployment_data.get('status', {})
    
    return {
        "name": deployment_data.get('metadata', {}).get('name'),
        "namespace": deployment_data.get('metadata', {}).get('namespace'),
        "replicas": {
            "spec": spec.get('replicas', 0),
            "ready": status.get('readyReplicas', 0),
            "available": status.get('availableReplicas', 0),
            "unavailable": status.get('unavailableReplicas', 0)
        },
        "conditions": status.get('conditions', []),
        "updated_at": status.get('updatedReplicas', 0)
    }

# Service 관련 API
@app.get("/services")
def get_all_services():
    """모든 Service 조회"""
    url = f"{settings.K8S_API}/api/v1/services"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/services/{namespace}")
def get_services_in_namespace(namespace: str):
    """특정 네임스페이스의 Service 조회"""
    url = f"{settings.K8S_API}/api/v1/namespaces/{namespace}/services"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

# Node 관련 API
@app.get("/nodes")
def get_nodes():
    """모든 Node 조회"""
    url = f"{settings.K8S_API}/api/v1/nodes"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/nodes/{node}")
def get_node(node: str):
    """특정 Node 조회"""
    url = f"{settings.K8S_API}/api/v1/nodes/{node}"
    r = requests.get(url, headers=settings.headers, verify=settings.VERIFY_SSL)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}
