# -*- coding: utf-8 -*-
"""
AIW Manifest Module
===================

/.well-known/aiw-manifest.json 생성.
PPR 함수: AI_make_manifest() 기반 구현.
"""

from typing import Any, Dict, List

from src.opstwin.config import settings


class ManifestBuilder:
    """AIW Manifest 빌더"""

    def __init__(self):
        self._schemas: List[str] = []
        self._endpoints: Dict[str, str] = {}
        self._auth: Dict[str, str] = {}

    def with_default_schemas(self) -> "ManifestBuilder":
        """기본 스키마 목록 설정"""
        self._schemas = [
            "telemetry.v1",
            "anomaly.v1",
            "policy.v1",
            "proposal.v1",
            "action.v1",
            "sim.v1",
        ]
        return self

    def with_default_endpoints(self) -> "ManifestBuilder":
        """기본 엔드포인트 목록 설정"""
        self._endpoints = {
            "schemas": "/schemas",
            "resource": "/r/{type}/{id}",
            "diff": "/diff",
            "subscribe": "/subscribe",
            "telemetry_ingest": "/telemetry/ingest",
            "sim_run": "/sim/run",
            "proposals": "/proposals",
            "actions": "/actions",
            "rollback": "/rollback/{action_id}",
        }
        return self

    def with_default_auth(self) -> "ManifestBuilder":
        """기본 인증 설정"""
        self._auth = {
            "read": "public_or_token",
            "write": "token_required",
            "action": "oauth2_or_jwt_rbac",
        }
        return self

    def build(self) -> Dict[str, Any]:
        """Manifest JSON 생성"""
        return {
            "aiw_version": settings.aiw_version,
            "service": {
                "name": settings.service_name,
                "version": settings.service_version,
            },
            "site_type": ["telemetry_stream", "action_policy", "sim_orbit"],
            "endpoints": self._endpoints,
            "schemas": self._schemas,
            "auth": self._auth,
            "limits": {
                "max_sse_connections": settings.max_sse_connections,
                "max_diff_page_size": settings.max_diff_page_size,
            },
        }


def build_manifest() -> Dict[str, Any]:
    """기본 설정으로 Manifest 생성 (편의 함수)"""
    return (
        ManifestBuilder()
        .with_default_schemas()
        .with_default_endpoints()
        .with_default_auth()
        .build()
    )
