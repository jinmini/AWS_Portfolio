from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("auth_service")

# .env 파일 로드
load_dotenv()

# 애플리케이션 시작 시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔐 Auth Service 시작")
    logger.info(f"🗄️ Database URL: {settings.DATABASE_URL}")
    yield
    logger.info("🔐 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Jinmini Auth Service",
    description="인증 및 사용자 관리 마이크로서비스",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gateway에서 이미 CORS 처리하지만 안전을 위해
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 헬스 체크
@app.get("/health")
async def health_check():
    """Auth Service 상태 확인"""
    return {
        "status": "healthy",
        "service": "Auth Service",
        "version": "1.0.0"
    }

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8101))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
