import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from app.domain.model.service_proxy import ServiceProxy
from contextlib import asynccontextmanager
from app.domain.model.service_type import ServiceType

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway_api")

# ✅ .env 파일 로드
load_dotenv()

# ✅ 애플리케이션 시작 시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    logger.info(f"🌐 환경: {os.getenv('NODE_ENV', 'development')}")
    logger.info(f"🔗 Auth Service: {os.getenv('AUTH_SERVICE_URL')}")
    logger.info(f"📝 Blog Service: {os.getenv('BLOG_SERVICE_URL')}")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

# ✅ FastAPI 앱 생성 
app = FastAPI(
    title="Jinmini Portfolio API Gateway",
    description="API Gateway for jinmini.com - 포트폴리오 & 블로그 마이크로서비스",
    version="1.0.0",
    lifespan=lifespan
)

# ✅ CORS 설정
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ 메인 라우터 생성
gateway_router = APIRouter(prefix="", tags=["Gateway"])

# ✅ 유틸리티 함수들
async def _extract_request_data(request: Request) -> tuple[Dict[str, str], bytes, Dict[str, Any]]:
    """요청에서 헤더, 바디, 쿼리 파라미터 추출"""
    # 헤더 추출
    headers = {name: value for name, value in request.headers.items()}
    
    # 바디 추출
    body = await request.body()
    
    # 쿼리 파라미터 추출
    query_params = dict(request.query_params)
    
    return headers, body, query_params

def _validate_service_type(service: str) -> ServiceType:
    """서비스 타입 검증"""
    try:
        return ServiceType(service)
    except ValueError:
        available_services = [s.value for s in ServiceType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service '{service}'. Available services: {available_services}"
        )

async def _proxy_request(method: str, service: ServiceType, path: str, request: Request) -> Response:
    """공통 프록시 요청 처리"""
    try:
        headers, body, query_params = await _extract_request_data(request)
        
        proxy = ServiceProxy(service_type=service)
        response = await proxy.request(
            method=method,
            path=path,
            headers=headers,
            body=body if body else None,
            query_params=query_params if query_params else None
        )
        
        # 응답 헤더에서 불필요한 헤더 제거
        excluded_response_headers = {'transfer-encoding', 'connection', 'keep-alive'}
        response_headers = {
            key: value for key, value in response.headers.items()
            if key.lower() not in excluded_response_headers
        }
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get('content-type')
        )
        
    except Exception as e:
        logger.error(f"💥 Proxy error for {method} /{service}/{path}: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal gateway error")

# ✅ 헬스 체크 엔드포인트
@gateway_router.get("/health", summary="헬스 체크")
async def health_check():
    """API Gateway 상태 확인"""
    return {
        "status": "healthy",
        "service": "API Gateway",
        "version": "1.0.0"
    }

# ✅ 서비스 상태 확인 엔드포인트
@gateway_router.get("/status", summary="전체 서비스 상태 확인")
async def service_status():
    """모든 마이크로서비스 상태 확인"""
    status = {"gateway": "healthy", "services": {}}
    
    for service_type in ServiceType:
        try:
            proxy = ServiceProxy(service_type=service_type)
            response = await proxy.request("GET", "health", {})
            status["services"][service_type.value] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code
            }
        except Exception as e:
            status["services"][service_type.value] = {
                "status": "error",
                "error": str(e)
            }
    
    return status

# ✅ HTTP 메서드별 라우터

@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(service: str, path: str, request: Request):
    """GET 요청 프록시"""
    service_type = _validate_service_type(service)
    return await _proxy_request("GET", service_type, path, request)

@gateway_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(service: str, path: str, request: Request):
    """POST 요청 프록시"""
    service_type = _validate_service_type(service)
    return await _proxy_request("POST", service_type, path, request)

@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: str, path: str, request: Request):
    """PUT 요청 프록시"""
    service_type = _validate_service_type(service)
    return await _proxy_request("PUT", service_type, path, request)

@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: str, path: str, request: Request):
    """DELETE 요청 프록시"""
    service_type = _validate_service_type(service)
    return await _proxy_request("DELETE", service_type, path, request)

@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: str, path: str, request: Request):
    """PATCH 요청 프록시"""
    service_type = _validate_service_type(service)
    return await _proxy_request("PATCH", service_type, path, request)

# ✅ 라우터 등록
app.include_router(gateway_router)

# ✅ 전역 예외 처리
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"❌ HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"💥 Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 