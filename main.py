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
    """Pod 삭제"""
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
    """Deployment 재시작"""
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
