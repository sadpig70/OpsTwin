# -*- coding: utf-8 -*-
"""
AIW Schema Registry Module
==========================

/schemas 엔드포인트 및 스키마 검증.
PPR 함수: AI_make_schema_registry() 기반 구현.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator


class SchemaRegistry:
    """JSON 스키마 레지스트리"""

    SCHEMAS_DIR = Path(__file__).parent.parent.parent.parent / "schemas"

    def __init__(self):
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._validators: Dict[str, Draft202012Validator] = {}

    def load_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """스키마 로드 (파일 또는 인메모리)"""
        if name in self._schemas:
            return self._schemas[name]

        # 파일에서 로드 시도
        schema_file = self.SCHEMAS_DIR / f"{name.replace('.', '_')}.json"
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)
                self.register_schema(name, schema)
                return schema

        # 내장 스키마 반환
        return self._get_builtin_schema(name)

    def register_schema(self, name: str, schema: Dict[str, Any]) -> None:
        """스키마 등록"""
        self._schemas[name] = schema
        self._validators[name] = Draft202012Validator(schema)

    def validate(self, name: str, data: Dict[str, Any]) -> List[str]:
        """데이터 검증, 에러 목록 반환"""
        if name not in self._validators:
            schema = self.load_schema(name)
            if schema is None:
                return [f"Unknown schema: {name}"]

        validator = self._validators.get(name)
        if validator is None:
            return [f"Validator not found: {name}"]

        errors = []
        for error in validator.iter_errors(data):
            errors.append(f"{error.json_path}: {error.message}")
        return errors

    def list_schemas(self) -> List[Dict[str, str]]:
        """등록된 스키마 목록"""
        builtin = ["telemetry.v1", "anomaly.v1", "policy.v1", "proposal.v1", "action.v1", "sim.v1"]
        return [{"name": name, "version": "v1"} for name in builtin]

    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """스키마 조회"""
        return self.load_schema(name)

    def _get_builtin_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """내장 스키마 반환"""
        schemas = {
            "telemetry.v1": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": "telemetry.v1",
                "type": "object",
                "required": ["event_id", "twin_id", "asset_id", "ts", "metrics"],
                "properties": {
                    "event_id": {"type": "string"},
                    "twin_id": {"type": "string"},
                    "asset_id": {"type": "string"},
                    "ts": {"type": "string", "format": "date-time"},
                    "metrics": {"type": "object", "additionalProperties": {"type": "number"}},
                    "tags": {"type": "object", "additionalProperties": {"type": "string"}},
                    "quality": {"type": "object"},
                },
            },
            "anomaly.v1": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": "anomaly.v1",
                "type": "object",
                "required": ["anomaly_id", "twin_id", "asset_id", "ts", "score", "kind"],
                "properties": {
                    "anomaly_id": {"type": "string"},
                    "twin_id": {"type": "string"},
                    "asset_id": {"type": "string"},
                    "ts": {"type": "string", "format": "date-time"},
                    "score": {"type": "number", "minimum": 0, "maximum": 1},
                    "kind": {
                        "type": "string",
                        "enum": ["drift", "spike", "outlier", "pattern", "missing"],
                    },
                    "features": {"type": "object"},
                    "recommended_next": {"type": "string"},
                },
            },
            "action.v1": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": "action.v1",
                "type": "object",
                "required": ["action_id", "twin_id", "target", "type"],
                "properties": {
                    "action_id": {"type": "string"},
                    "proposal_id": {"type": "string"},
                    "twin_id": {"type": "string"},
                    "target": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["set_parameter", "restart", "scale", "deploy", "rollback"],
                    },
                    "params": {"type": "object"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "running", "success", "failed", "cancelled"],
                    },
                },
            },
        }
        schema = schemas.get(name)
        if schema:
            self.register_schema(name, schema)
        return schema


# 싱글톤 인스턴스
schema_registry = SchemaRegistry()
