from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from config.settings import settings, get_cluster_config
from config.cluster_manager import ClusterManager

# Pydantic 모델 정의

class SetTokenRequest(BaseModel):
    cluster_id: str
    token: str
    host: str
    port: int = 6443
    verify_ssl: bool = False

class SSHTokenRequest(BaseModel):
    ssh_host: str
    ssh_port: int = 22
    ssh_username: str = "root"
    ssh_password: str
    k8s_host: str
    k8s_port: int = 6443
    cluster_name: str
    service_account: str = "dashboard-admin"
    namespace: str = "default"
    verify_ssl: bool = False

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

# 클러스터 매니저 인스턴스
cluster_manager = ClusterManager()

@app.get("/")
def root():
    return {"message": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ==================== 조회 API ====================

@app.get("/namespaces")
def get_namespaces(cluster_id: Optional[str] = None):
    """모든 네임스페이스 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/api/v1/namespaces"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/namespaces/{namespace}")
def get_namespace(namespace: str, cluster_id: Optional[str] = None):
    """특정 네임스페이스 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/api/v1/namespaces/{namespace}"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/pods")
def get_all_pods(cluster_id: Optional[str] = None):
    """모든 Pod 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/api/v1/pods"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/pods/{namespace}")
def get_pods_in_namespace(namespace: str, cluster_id: Optional[str] = None):
    """특정 네임스페이스의 Pod 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/api/v1/namespaces/{namespace}/pods"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/pods/{namespace}/{pod}")
def get_pod(namespace: str, pod: str, cluster_id: Optional[str] = None):
    """특정 Pod 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/api/v1/namespaces/{namespace}/pods/{pod}"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/deployments")
def get_all_deployments(cluster_id: Optional[str] = None):
    """모든 Deployment 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/deployments"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/deployments/{namespace}")
def get_deployments_in_namespace(namespace: str, cluster_id: Optional[str] = None):
    """특정 네임스페이스의 Deployment 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/deployments"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/deployments/{namespace}/{deployment}")
def get_deployment(namespace: str, deployment: str, cluster_id: Optional[str] = None):
    """특정 Deployment 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/daemonsets")
def get_all_daemonsets(cluster_id: Optional[str] = None):
    """모든 DaemonSet 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/daemonsets"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/daemonsets/{namespace}")
def get_daemonsets_in_namespace(namespace: str, cluster_id: Optional[str] = None):
    """특정 네임스페이스의 DaemonSet 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/daemonsets"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/daemonsets/{namespace}/{daemonset}")
def get_daemonset(namespace: str, daemonset: str, cluster_id: Optional[str] = None):
    """특정 DaemonSet 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/daemonsets/{daemonset}"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/statefulsets")
def get_all_statefulsets(cluster_id: Optional[str] = None):
    """모든 StatefulSet 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/statefulsets"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/statefulsets/{namespace}")
def get_statefulsets_in_namespace(namespace: str, cluster_id: Optional[str] = None):
    """특정 네임스페이스의 StatefulSet 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/statefulsets"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

@app.get("/statefulsets/{namespace}/{statefulset}")
def get_statefulset(namespace: str, statefulset: str, cluster_id: Optional[str] = None):
    """특정 StatefulSet 조회"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/statefulsets/{statefulset}"
    r = requests.get(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {"status": r.status_code, "response": r.json()}

# ==================== 삭제 API ====================

@app.delete("/pods/{namespace}/{pod}")
def delete_pod(namespace: str, pod: str, cluster_id: Optional[str] = None):
    """Pod 삭제"""
    cluster_config = get_cluster_config(cluster_id)
    url = f"{cluster_config['api_url']}/api/v1/namespaces/{namespace}/pods/{pod}"
    r = requests.delete(url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
    return {"status": r.status_code, "response": r.json()}

# ==================== 롤아웃 API ====================

@app.post("/deployments/{namespace}/{deployment}/rollout")
def rollout_deployment(namespace: str, deployment: str, cluster_id: Optional[str] = None, timeout: int = 30):
    """Deployment 롤아웃"""
    cluster_config = get_cluster_config(cluster_id)
    return _rollout_workload("deployment", namespace, deployment, cluster_config, timeout)

@app.post("/daemonsets/{namespace}/{daemonset}/rollout")
def rollout_daemonset(namespace: str, daemonset: str, cluster_id: Optional[str] = None, timeout: int = 30):
    """DaemonSet 롤아웃"""
    cluster_config = get_cluster_config(cluster_id)
    return _rollout_workload("daemonset", namespace, daemonset, cluster_config, timeout)

@app.post("/statefulsets/{namespace}/{statefulset}/rollout")
def rollout_statefulset(namespace: str, statefulset: str, cluster_id: Optional[str] = None, timeout: int = 30):
    """StatefulSet 롤아웃"""
    cluster_config = get_cluster_config(cluster_id)
    return _rollout_workload("statefulset", namespace, statefulset, cluster_config, timeout)

def _rollout_workload(workload_type: str, namespace: str, name: str, cluster_config: dict, timeout: int = 30):
    """워크로드 롤아웃 공통 함수"""
    import time
    
    # 1. 워크로드 재시작 요청
    url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/{workload_type}s/{name}"
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
    r = requests.patch(url, headers={**cluster_config['headers'], "Content-Type": "application/merge-patch+json"},
                       json=patch, verify=cluster_config['verify_ssl'])
    
    if r.status_code != 200:
        return {"status": "error", "message": "Rollout 요청 실패", "details": r.json()}
    
    # 2. 상태 모니터링
    start_time = time.time()
    check_interval = 1  # 1초마다 체크
    
    while time.time() - start_time < timeout:
        # 워크로드 상태 확인
        status_url = f"{cluster_config['api_url']}/apis/apps/v1/namespaces/{namespace}/{workload_type}s/{name}"
        status_r = requests.get(status_url, headers=cluster_config['headers'], verify=cluster_config['verify_ssl'])
        
        if status_r.status_code == 200:
            workload_data = status_r.json()
            spec_replicas = workload_data.get('spec', {}).get('replicas', 0)
            ready_replicas = workload_data.get('status', {}).get('readyReplicas', 0)
            available_replicas = workload_data.get('status', {}).get('availableReplicas', 0)
            
            # 모든 조건이 만족되면 성공
            if (ready_replicas == spec_replicas and 
                available_replicas == spec_replicas and 
                spec_replicas > 0):
                return {
                    "status": "success",
                    "message": f"{workload_type.title()} Rollout 완료",
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
        "message": f"{workload_type.title()} Rollout이 {timeout}초 내에 완료되지 않았습니다",
        "duration": timeout
    }

# ==================== 클러스터 토큰 관리 API ====================


@app.get("/clusters")
def list_clusters():
    """저장된 클러스터 목록 조회"""
    return cluster_manager.list_clusters()

@app.get("/clusters/{cluster_id}")
def get_cluster_info(cluster_id: str):
    """특정 클러스터 정보 조회"""
    try:
        return cluster_manager.get_cluster_info(cluster_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/clusters/set-token")
def set_cluster_token(request: SetTokenRequest):
    """기존 토큰을 직접 설정"""
    try:
        # 토큰 유효성 검증
        api_url = f"https://{request.host}:{request.port}"
        test_headers = {"Authorization": f"Bearer {request.token}"}
        test_url = f"{api_url}/api/v1/namespaces"
        test_response = requests.get(test_url, headers=test_headers, verify=request.verify_ssl, timeout=10)
        
        if test_response.status_code != 200:
            raise Exception(f"토큰이 유효하지 않습니다: {test_response.status_code} - {test_response.text}")
        
        # 클러스터 설정 저장
        cluster_manager.save_cluster_config(request.cluster_id, request.host, request.port, request.token, request.verify_ssl)
        return {"status": "success", "message": f"클러스터 '{request.cluster_id}' 토큰이 설정되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/clusters/ssh-token")
def create_token_via_ssh(request: SSHTokenRequest):
    """SSH를 통해 클러스터 VM에 접속하여 토큰 생성 및 저장"""
    try:
        token = cluster_manager.get_token_via_ssh(
            request.ssh_host, request.ssh_port, request.ssh_username, request.ssh_password,
            request.k8s_host, request.k8s_port, request.service_account, request.namespace
        )
        cluster_manager.save_cluster_config(request.cluster_name, request.k8s_host, request.k8s_port, token, request.verify_ssl)
        return {
            "status": "success", 
            "message": f"SSH를 통해 클러스터 '{request.cluster_name}' 토큰이 생성되고 저장되었습니다.",
            "ssh_host": request.ssh_host,
            "k8s_host": request.k8s_host
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"서버 시작: http://{settings.HOST}:{settings.PORT}")
    print(f"API 문서: http://{settings.HOST}:{settings.PORT}/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
