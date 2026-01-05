# -*- coding: utf-8 -*-
"""
Phase 0.1: AIW Protocol PPR 함수 정의
=====================================

AIW (AI Web) 프로토콜 관련 PPR 함수 모음.
Manifest, DiffStream, SchemaRegistry 3대 모듈의 12개 함수 정의.

Gantree Reference: OpsTwin_Gantree.md → AIW_Protocol
"""

from dataclasses import dataclass
from typing import Any, Dict, List

# =============================================================================
# 데이터 타입 정의
# =============================================================================

@dataclass
class ManifestConfig:
    """Manifest 설정 데이터 타입"""
    aiw_version: str = "1.0"
    service_name: str = "OpsTwin"
    service_version: str = "0.2"
    site_types: List[str] = None

    def __post_init__(self):
        if self.site_types is None:
            self.site_types = ["telemetry_stream", "action_policy", "sim_orbit"]


@dataclass
class EndpointConfig:
    """엔드포인트 설정 데이터 타입"""
    path: str
    method: str = "GET"
    description: str = ""


@dataclass
class DiffEvent:
    """Diff 이벤트 데이터 타입"""
    event_type: str
    timestamp: str
    twin_id: str
    event_id: str
    data_ref: Dict[str, str]


# =============================================================================
# Manifest 함수 (ManifestFunction)
# =============================================================================

def AI_make_manifest(config: ManifestConfig = None) -> Dict[str, Any]:
    """
    Gantree: AIW_Protocol → Manifest
    
    Purpose:
        AIW Manifest JSON 생성. 서비스가 제공하는 리소스/스키마/엔드포인트/권한을 선언.
    
    Inputs:
        - config: ManifestConfig - Manifest 설정 (선택)
    
    Outputs:
        - manifest: Dict - /.well-known/aiw-manifest.json 형식의 딕셔너리
    
    Dependencies:
        - AI_make_manifest_schema()
        - AI_make_endpoint_registry()
        - AI_make_capability_declaration()
    
    Status: Design
    """
    if config is None:
        config = ManifestConfig()

    manifest = {
        "aiw_version": config.aiw_version,
        "service": {
            "name": config.service_name,
            "version": config.service_version
        },
        "site_type": config.site_types,
        "endpoints": AI_make_endpoint_registry(),
        "schemas": AI_make_manifest_schema(),
        "auth": AI_make_capability_declaration(),
        "limits": {
            "max_sse_connections": 1000,
            "max_diff_page_size": 5000
        }
    }
    return manifest


def AI_make_manifest_schema() -> List[str]:
    """
    Gantree: Manifest → ManifestSchema
    
    Purpose:
        Manifest에 포함될 스키마 목록 정의.
    
    Inputs:
        없음
    
    Outputs:
        - schemas: List[str] - 지원하는 스키마 버전 목록
    
    Dependencies:
        없음
    
    Status: Design
    """
    return [
        "telemetry.v1",
        "anomaly.v1",
        "policy.v1",
        "proposal.v1",
        "action.v1",
        "sim.v1"
    ]


def AI_make_endpoint_registry() -> Dict[str, str]:
    """
    Gantree: Manifest → EndpointRegistry
    
    Purpose:
        AIW 서비스의 엔드포인트 레지스트리 생성.
    
    Inputs:
        없음
    
    Outputs:
        - endpoints: Dict[str, str] - 엔드포인트 이름과 경로 매핑
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "schemas": "/schemas",
        "resource": "/r/{type}/{id}",
        "diff": "/diff",
        "subscribe": "/subscribe",
        "telemetry_ingest": "/telemetry/ingest",
        "sim_run": "/sim/run",
        "proposals": "/proposals",
        "actions": "/actions",
        "rollback": "/rollback/{action_id}"
    }


def AI_make_capability_declaration() -> Dict[str, str]:
    """
    Gantree: Manifest → CapabilityDeclaration
    
    Purpose:
        서비스의 인증/권한 요구사항 선언.
    
    Inputs:
        없음
    
    Outputs:
        - auth: Dict[str, str] - 권한별 인증 요구사항
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "read": "public_or_token",
        "write": "token_required",
        "action": "oauth2_or_jwt_rbac"
    }


# =============================================================================
# DiffStream 함수 (DiffStreamFunction)
# =============================================================================

def AI_make_diff_stream(since_cursor: str = None, limit: int = 100) -> Dict[str, Any]:
    """
    Gantree: AIW_Protocol → DiffStream
    
    Purpose:
        Diff 스트리밍 응답 생성. 변경분 동기화의 핵심 함수.
    
    Inputs:
        - since_cursor: str - 시작 커서 위치
        - limit: int - 최대 이벤트 수
    
    Outputs:
        - diff_response: Dict - since, next_cursor, events를 포함하는 응답
    
    Dependencies:
        - AI_make_diff_engine()
        - AI_make_cursor_manager()
    
    Status: Design
    """
    cursor_manager = AI_make_cursor_manager()
    current_cursor = since_cursor or cursor_manager.get("initial_cursor", "cursor_000000")

    # Diff 엔진으로 이벤트 조회
    events = AI_make_diff_engine(current_cursor, limit)

    # 다음 커서 계산
    next_cursor = f"cursor_{int(current_cursor.split('_')[1]) + len(events):06d}" if events else current_cursor

    return {
        "since": current_cursor,
        "next_cursor": next_cursor,
        "events": events
    }


def AI_make_diff_engine(since_cursor: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Gantree: DiffStream → DiffEngine
    
    Purpose:
        커서 이후의 변경 이벤트를 조회하는 엔진.
    
    Inputs:
        - since_cursor: str - 시작 커서
        - limit: int - 최대 조회 수
    
    Outputs:
        - events: List[Dict] - 이벤트 목록
    
    Dependencies:
        없음 (실제 구현 시 EventStore 연동)
    
    Status: Design
    """
    # 설계 단계: 빈 이벤트 목록 반환 (실제 구현 시 EventStore 조회)
    return []


def AI_make_sse_publisher(event: DiffEvent) -> str:
    """
    Gantree: DiffStream → SSEPublisher
    
    Purpose:
        Server-Sent Events 형식으로 이벤트 발행.
    
    Inputs:
        - event: DiffEvent - 발행할 이벤트
    
    Outputs:
        - sse_message: str - SSE 형식 메시지
    
    Dependencies:
        없음
    
    Status: Design
    """
    import json

    payload = {
        "type": event.event_type,
        "ts": event.timestamp,
        "twin_id": event.twin_id,
        "id": event.event_id,
        "data_ref": event.data_ref
    }

    # SSE 형식: data: {json}\n\n
    return f"data: {json.dumps(payload)}\n\n"


def AI_make_cursor_manager() -> Dict[str, Any]:
    """
    Gantree: DiffStream → CursorManager
    
    Purpose:
        구독자별 커서 상태 관리.
    
    Inputs:
        없음
    
    Outputs:
        - cursor_state: Dict - 커서 관리 상태 (초기 설정)
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "initial_cursor": "cursor_000000",
        "cursor_format": "cursor_{:06d}",
        "persistence": "redis",  # 실제 구현 시 Redis/DB 연동
        "ttl_seconds": 86400  # 24시간
    }


# =============================================================================
# SchemaRegistry 함수 (SchemaRegistryFunction)
# =============================================================================

def AI_make_schema_registry() -> Dict[str, Any]:
    """
    Gantree: AIW_Protocol → SchemaRegistry
    
    Purpose:
        스키마 레지스트리 전체 구조 생성.
    
    Inputs:
        없음
    
    Outputs:
        - registry: Dict - 스키마 레지스트리 메타데이터
    
    Dependencies:
        - AI_make_telemetry_schema()
        - AI_make_action_schema()
        - AI_make_policy_schema()
    
    Status: Design
    """
    return {
        "version": "1.0",
        "schemas": {
            "telemetry.v1": AI_make_telemetry_schema(),
            "action.v1": AI_make_action_schema(),
            "policy.v1": AI_make_policy_schema()
        },
        "compatibility": "backward"
    }


def AI_make_telemetry_schema() -> Dict[str, Any]:
    """
    Gantree: SchemaRegistry → TelemetrySchema
    
    Purpose:
        telemetry.v1 JSON 스키마 정의.
    
    Inputs:
        없음
    
    Outputs:
        - schema: Dict - JSON Schema 형식의 telemetry.v1 스키마
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "telemetry.v1",
        "type": "object",
        "required": ["event_id", "twin_id", "asset_id", "ts", "metrics"],
        "properties": {
            "event_id": {"type": "string", "description": "전역 고유 이벤트 ID"},
            "twin_id": {"type": "string", "description": "트윈 식별자"},
            "asset_id": {"type": "string", "description": "자산 식별자"},
            "ts": {"type": "string", "format": "date-time", "description": "RFC3339 타임스탬프"},
            "metrics": {
                "type": "object",
                "additionalProperties": {"type": "number"},
                "description": "메트릭 키-값 쌍"
            },
            "tags": {
                "type": "object",
                "additionalProperties": {"type": "string"},
                "description": "태그 키-값 쌍"
            },
            "quality": {
                "type": "object",
                "properties": {
                    "data_quality_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "missing_rate": {"type": "number", "minimum": 0, "maximum": 1},
                    "source": {"type": "string"}
                },
                "description": "데이터 품질 지표"
            }
        }
    }


def AI_make_action_schema() -> Dict[str, Any]:
    """
    Gantree: SchemaRegistry → ActionSchema
    
    Purpose:
        action.v1 JSON 스키마 정의.
    
    Inputs:
        없음
    
    Outputs:
        - schema: Dict - JSON Schema 형식의 action.v1 스키마
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "action.v1",
        "type": "object",
        "required": ["action_id", "twin_id", "target", "type"],
        "properties": {
            "action_id": {"type": "string", "description": "액션 고유 ID"},
            "proposal_id": {"type": "string", "description": "연관 제안 ID"},
            "twin_id": {"type": "string", "description": "트윈 식별자"},
            "target": {"type": "string", "description": "대상 자산 URI (asset://...)"},
            "type": {
                "type": "string",
                "enum": ["set_parameter", "restart", "scale", "deploy", "rollback"],
                "description": "액션 타입"
            },
            "params": {"type": "object", "description": "액션 파라미터"},
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium"
            },
            "execution_mode": {
                "type": "string",
                "enum": ["sync", "async"],
                "default": "async"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "running", "success", "failed", "cancelled"]
            },
            "idempotency_key": {"type": "string", "description": "중복 실행 방지 키"}
        }
    }


def AI_make_policy_schema() -> Dict[str, Any]:
    """
    Gantree: SchemaRegistry → PolicySchema
    
    Purpose:
        policy.v1 JSON 스키마 정의.
    
    Inputs:
        없음
    
    Outputs:
        - schema: Dict - JSON Schema 형식의 policy.v1 스키마
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "policy.v1",
        "type": "object",
        "required": ["policy_id", "scope"],
        "properties": {
            "policy_id": {"type": "string", "description": "정책 고유 ID"},
            "scope": {
                "type": "object",
                "properties": {
                    "twin_id": {"type": "string"},
                    "asset_id": {"type": "string"},
                    "process": {"type": "string"}
                },
                "description": "정책 적용 범위"
            },
            "roles_permissions": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "description": "RBAC 역할-권한 매핑"
            },
            "decision_thresholds": {
                "type": "object",
                "properties": {
                    "auto_execute_min": {"type": "number", "minimum": 0, "maximum": 1},
                    "approve_min": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "description": "자동실행/승인 임계값"
            },
            "rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "if": {"type": "string"},
                        "then": {"type": "string"}
                    }
                },
                "description": "조건부 규칙 목록"
            },
            "safety_constraints": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "forbid": {"type": "string"}
                    }
                },
                "description": "안전 제약 조건"
            }
        }
    }
