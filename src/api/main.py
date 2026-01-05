# -*- coding: utf-8 -*-
"""
OpsTwin FastAPI Application
===========================

메인 FastAPI 앱 및 라우터 설정.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import diff, manifest, sim, telemetry
from src.opstwin.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """앱 생명주기 관리"""
    # 시작 시
    print(f"🚀 Starting OpsTwin API v{settings.service_version}")

    # DB 연결 (선택적)
    try:
        from src.opstwin.database import database
        from src.opstwin.redis_client import redis_client

        await redis_client.connect()
        print("✅ Redis connected")

        await database.connect()
        print("✅ TimescaleDB connected")
    except Exception as e:
        print(f"⚠️ DB connection skipped (MVP mode): {e}")

    yield

    # 종료 시
    try:
        from src.opstwin.database import database
        from src.opstwin.redis_client import redis_client

        await redis_client.disconnect()
        await database.disconnect()
    except Exception:
        pass

    print("👋 Shutting down OpsTwin API")


app = FastAPI(
    title="OpsTwin API",
    description="Industrial Digital Twin + Quantum Simulation Integration Platform",
    version=settings.service_version,
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 등록

app.include_router(manifest.router)
app.include_router(diff.router)
app.include_router(telemetry.router)
app.include_router(sim.router)


@app.get("/health", tags=["Health"])
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": settings.service_name}
