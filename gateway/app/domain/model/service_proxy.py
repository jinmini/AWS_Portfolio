from typing import Optional, Dict, Any
from fastapi import HTTPException
import httpx
from app.domain.model.service_type import SERVICE_URLS, ServiceType
import logging 
import json

logger = logging.getLogger(__name__)

class ServiceProxy:
    """마이크로서비스 프록시 클래스"""
    
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.base_url = SERVICE_URLS[service_type]
        self.timeout = 30.0  # 30초 타임아웃
        
        if not self.base_url:
            raise ValueError(f"Service URL not configured for {service_type}")

    def _filter_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """클라이언트 헤더를 필터링하여 백엔드로 전달할 헤더만 추출"""
        # 제외할 헤더들
        excluded_headers = {
            'host', 'content-length', 'connection', 'accept-encoding',
            'user-agent', 'origin', 'referer'
        }
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() not in excluded_headers:
                filtered[key] = value
                
        return filtered

    async def request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        백엔드 서비스로 HTTP 요청을 프록시
        
        Args:
            method: HTTP 메서드 (GET, POST, PUT, DELETE, PATCH)
            path: 요청 경로
            headers: HTTP 헤더
            body: 요청 바디
            query_params: 쿼리 파라미터
            
        Returns:
            httpx.Response: 백엔드 서비스 응답
            
        Raises:
            HTTPException: HTTP 에러 발생 시
        """
        # URL 구성
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # 헤더 필터링
        headers_to_send = self._filter_headers(headers or {})
        
        logger.info(f"🔄 Proxying {method} {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers_to_send,
                    content=body,
                    params=query_params
                )
                
                logger.info(f"✅ Response {response.status_code} from {self.service_type}")
                return response
                
            except httpx.TimeoutException:
                logger.error(f"⏰ Timeout calling {self.service_type} service")
                raise HTTPException(
                    status_code=504,
                    detail=f"Timeout calling {self.service_type} service"
                )
            except httpx.ConnectError:
                logger.error(f"🔌 Connection error to {self.service_type} service")
                raise HTTPException(
                    status_code=503,
                    detail=f"Service {self.service_type} unavailable"
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ HTTP error {e.response.status_code} from {self.service_type}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Error from {self.service_type} service"
                )
            except Exception as e:
                logger.error(f"💥 Unexpected error calling {self.service_type}: {str(e)}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Bad gateway - {self.service_type} service error"
                )
