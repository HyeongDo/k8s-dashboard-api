import os
from typing import Optional

class Settings:
    """애플리케이션 설정 클래스"""
    
    # Kubernetes API 설정
    K8S_API: str = os.getenv("K8S_API", "https://172.10.40.93:6443")
    K8S_TOKEN: Optional[str] = os.getenv("K8S_TOKEN")
    VERIFY_SSL: bool = os.getenv("VERIFY_SSL", "false").lower() == "true"
    
    # 애플리케이션 설정
    APP_NAME: str = "Kubernetes Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 서버 설정
    HOST: str = os.getenv("HOST", "127.0.0.1")  # 기본값을 localhost로 변경
    PORT: int = int(os.getenv("PORT", "8000"))
    
    def __init__(self):
        """설정 초기화 및 검증"""
        if not self.K8S_TOKEN:
            raise ValueError("K8S_TOKEN 환경변수가 설정되지 않았습니다.")
    
    @property
    def headers(self) -> dict:
        """Kubernetes API 요청용 헤더 반환"""
        return {"Authorization": f"Bearer {self.K8S_TOKEN}"}

# 전역 설정 인스턴스
settings = Settings()
