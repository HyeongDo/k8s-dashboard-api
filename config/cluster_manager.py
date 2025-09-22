import json
import requests
import paramiko
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.settings import settings

class ClusterManager:
    """클러스터 토큰 생성 및 관리 클래스"""
    
    def __init__(self):
        self.clusters_file = Path(settings.CLUSTERS_CONFIG_PATH)
        self._ensure_clusters_config_exists()
    
    def _ensure_clusters_config_exists(self):
        """클러스터 설정 파일이 없으면 생성"""
        if not self.clusters_file.exists():
            self.clusters_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.clusters_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
    
    def validate_token(self, host: str, port: int, token: str, verify_ssl: bool = False) -> bool:
        """토큰 유효성 검증"""
        try:
            api_url = f"https://{host}:{port}"
            test_headers = {"Authorization": f"Bearer {token}"}
            test_url = f"{api_url}/api/v1/namespaces"
            test_response = requests.get(test_url, headers=test_headers, verify=verify_ssl, timeout=10)
            
            return test_response.status_code == 200
        except:
            return False
    
    def get_token_via_ssh(self, ssh_host: str, ssh_port: int, ssh_username: str, ssh_password: str, 
                         k8s_host: str, k8s_port: int, service_account: str = "dashboard-admin", 
                         namespace: str = "default") -> str:
        """SSH를 통해 클러스터 VM에 접속하여 토큰 획득"""
        try:
            print(f"SSH 연결 시도: {ssh_username}@{ssh_host}:{ssh_port}")
            
            # SSH 클라이언트 생성
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # SSH 연결
            ssh.connect(
                hostname=ssh_host,
                port=ssh_port,
                username=ssh_username,
                password=ssh_password,
                timeout=30
            )
            
            print(f"SSH 연결 성공")
            
            # 1. ServiceAccount가 존재하는지 확인
            check_sa_cmd = f"kubectl get serviceaccount {service_account} -n {namespace} --no-headers"
            stdin, stdout, stderr = ssh.exec_command(check_sa_cmd)
            sa_exists = stdout.channel.recv_exit_status() == 0
            
            if not sa_exists:
                print(f"ServiceAccount 생성 중: {service_account}")
                # ServiceAccount 생성
                create_sa_cmd = f"kubectl create serviceaccount {service_account} -n {namespace}"
                stdin, stdout, stderr = ssh.exec_command(create_sa_cmd)
                exit_status = stdout.channel.recv_exit_status()
                
                if exit_status != 0:
                    error_output = stderr.read().decode()
                    if "already exists" not in error_output:
                        raise Exception(f"ServiceAccount 생성 실패: {error_output}")
                else:
                    print(f"ServiceAccount 생성 완료")
            
            # 2. ClusterRoleBinding 확인 및 생성
            binding_name = "dashboard-admin"
            check_binding_cmd = f"kubectl get clusterrolebinding {binding_name} --no-headers"
            stdin, stdout, stderr = ssh.exec_command(check_binding_cmd)
            binding_exists = stdout.channel.recv_exit_status() == 0
            
            if not binding_exists:
                print(f"ClusterRoleBinding 생성 중: {binding_name}")
                create_binding_cmd = f"""kubectl create clusterrolebinding {binding_name} \\
                    --clusterrole=cluster-admin \\
                    --serviceaccount={namespace}:{service_account}"""
                stdin, stdout, stderr = ssh.exec_command(create_binding_cmd)
                exit_status = stdout.channel.recv_exit_status()
                
                if exit_status != 0:
                    error_output = stderr.read().decode()
                    if "already exists" not in error_output:
                        raise Exception(f"ClusterRoleBinding 생성 실패: {error_output}")
                else:
                    print(f"ClusterRoleBinding 생성 완료")
            
            # 3. 토큰 생성
            print(f"토큰 생성 중...")
            token_cmd = f"kubectl create token {service_account} -n {namespace}"
            stdin, stdout, stderr = ssh.exec_command(token_cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status != 0:
                error_output = stderr.read().decode()
                raise Exception(f"토큰 생성 실패: {error_output}")
            
            token = stdout.read().decode().strip()
            if not token:
                raise Exception("토큰이 비어있습니다.")
            
            print(f"토큰 생성 완료")
            
            # 4. 토큰 유효성 검증
            if self.validate_token(k8s_host, k8s_port, token):
                print(f"토큰 유효성 검증 완료")
                return token
            else:
                raise Exception("생성된 토큰이 유효하지 않습니다.")
                
        except paramiko.AuthenticationException:
            raise Exception("SSH 인증 실패: 사용자명 또는 비밀번호가 올바르지 않습니다.")
        except paramiko.SSHException as e:
            raise Exception(f"SSH 연결 오류: {str(e)}")
        except Exception as e:
            raise Exception(f"SSH를 통한 토큰 획득 실패: {str(e)}")
        finally:
            try:
                ssh.close()
            except:
                pass
    
    
    def save_cluster_config(self, cluster_name: str, host: str, port: int, token: str, verify_ssl: bool = False):
        """클러스터 설정을 파일에 저장"""
        try:
            # 기존 클러스터 설정 로드
            if self.clusters_file.exists():
                with open(self.clusters_file, 'r', encoding='utf-8') as f:
                    clusters = json.load(f)
            else:
                clusters = {}
            
            # 새 클러스터 설정 추가
            clusters[cluster_name] = {
                "api_url": f"https://{host}:{port}",
                "token": token,
                "verify_ssl": verify_ssl,
                "host": host,
                "port": port
            }
            
            # 파일에 저장
            with open(self.clusters_file, 'w', encoding='utf-8') as f:
                json.dump(clusters, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"클러스터 설정 저장 실패: {str(e)}")
    
    def list_clusters(self) -> List[Dict[str, Any]]:
        """저장된 클러스터 목록 반환"""
        try:
            if not self.clusters_file.exists():
                return []
            
            with open(self.clusters_file, 'r', encoding='utf-8') as f:
                clusters = json.load(f)
            
            result = []
            for cluster_id, config in clusters.items():
                result.append({
                    "cluster_id": cluster_id,
                    "api_url": config["api_url"],
                    "host": config["host"],
                    "port": config["port"],
                    "verify_ssl": config.get("verify_ssl", False)
                })
            
            return result
            
        except Exception as e:
            raise Exception(f"클러스터 목록 조회 실패: {str(e)}")
    
    def get_cluster_info(self, cluster_id: str) -> Dict[str, Any]:
        """특정 클러스터 정보 반환"""
        try:
            if not self.clusters_file.exists():
                raise Exception("클러스터 설정 파일이 없습니다.")
            
            with open(self.clusters_file, 'r', encoding='utf-8') as f:
                clusters = json.load(f)
            
            if cluster_id not in clusters:
                raise Exception(f"클러스터 '{cluster_id}'를 찾을 수 없습니다.")
            
            config = clusters[cluster_id]
            return {
                "cluster_id": cluster_id,
                "api_url": config["api_url"],
                "host": config["host"],
                "port": config["port"],
                "verify_ssl": config.get("verify_ssl", False)
            }
            
        except Exception as e:
            raise Exception(f"클러스터 정보 조회 실패: {str(e)}")
    
    
    def test_cluster_connection(self, cluster_id: str) -> bool:
        """클러스터 연결 테스트"""
        try:
            from config.settings import get_cluster_config
            cluster_config = get_cluster_config(cluster_id)
            
            # 간단한 API 호출로 연결 테스트
            test_url = f"{cluster_config['api_url']}/api/v1/namespaces"
            response = requests.get(
                test_url, 
                headers=cluster_config['headers'], 
                verify=cluster_config['verify_ssl'],
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
