import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

class Settings:
    """애플리케이션 설정 클래스"""
    
    # 애플리케이션 설정
    APP_NAME: str = "Kubernetes Dashboard API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 서버 설정
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 클러스터 설정 파일 경로
    CLUSTERS_CONFIG_PATH: str = os.getenv("CLUSTERS_CONFIG_PATH", "config/clusters.json")
    
    def __init__(self):
        """설정 초기화"""
        # 클러스터 설정 파일이 없으면 생성
        self._ensure_clusters_config_exists()
    
    def _ensure_clusters_config_exists(self):
        """클러스터 설정 파일이 없으면 생성"""
        clusters_file = Path(self.CLUSTERS_CONFIG_PATH)
        if not clusters_file.exists():
            clusters_file.parent.mkdir(parents=True, exist_ok=True)
            with open(clusters_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

# 전역 설정 인스턴스
settings = Settings()

def get_default_cluster_id() -> str:
    """기본 클러스터 ID를 가져오는 함수 (가장 최근에 설정된 클러스터)"""
    clusters_file = Path(settings.CLUSTERS_CONFIG_PATH)
    
    if not clusters_file.exists():
        return "default"
    
    with open(clusters_file, 'r', encoding='utf-8') as f:
        clusters = json.load(f)
    
    # 클러스터가 없으면 default 반환
    if not clusters:
        return "default"
    
    # 마지막에 추가된 클러스터를 기본값으로 사용
    # (Python 3.7+에서는 dict가 삽입 순서를 유지함)
    return list(clusters.keys())[-1]

def get_cluster_config(cluster_id: Optional[str] = None) -> Dict[str, Any]:
    """클러스터 설정을 가져오는 함수"""
    if cluster_id is None:
        cluster_id = get_default_cluster_id()
    
    clusters_file = Path(settings.CLUSTERS_CONFIG_PATH)
    
    if not clusters_file.exists():
        raise ValueError(f"클러스터 설정 파일이 없습니다: {settings.CLUSTERS_CONFIG_PATH}")
    
    with open(clusters_file, 'r', encoding='utf-8') as f:
        clusters = json.load(f)
    
    if cluster_id not in clusters:
        raise ValueError(f"클러스터 '{cluster_id}'를 찾을 수 없습니다.")
    
    cluster_config = clusters[cluster_id]
    
    return {
        'api_url': cluster_config['api_url'],
        'headers': {"Authorization": f"Bearer {cluster_config['token']}"},
        'verify_ssl': cluster_config.get('verify_ssl', False)
    }
