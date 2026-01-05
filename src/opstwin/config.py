# -*- coding: utf-8 -*-
"""
OpsTwin Configuration
=====================

환경변수 기반 설정 관리.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """OpsTwin 전역 설정"""

    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # 데이터베이스 설정
    database_url: str = "postgresql://opstwin:password@localhost:5432/opstwin"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Kafka 설정
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "opstwin-processor"

    # Redis 설정
    redis_url: str = "redis://localhost:6379/0"

    # 인증 설정
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # 양자 시뮬레이션 설정
    qiskit_backend: str = "aer_simulator"
    ibm_quantum_token: Optional[str] = None

    # AIW 설정
    aiw_version: str = "1.0"
    service_name: str = "OpsTwin"
    service_version: str = "0.2"

    # 스트리밍 설정
    max_sse_connections: int = 1000
    max_diff_page_size: int = 5000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """싱글톤 설정 인스턴스 반환"""
    return Settings()


settings = get_settings()
