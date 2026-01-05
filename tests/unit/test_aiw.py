# -*- coding: utf-8 -*-
"""
AIW Module Unit Tests
=====================
"""

import pytest
from src.opstwin.aiw.manifest import ManifestBuilder, build_manifest
from src.opstwin.aiw.diff_stream import DiffEngine, CursorManager
from src.opstwin.aiw.schema_registry import SchemaRegistry
from src.opstwin.aiw.sse_publisher import SSEPublisher, SSEMessage


class TestManifest:
    """Manifest 테스트"""
    
    def test_build_manifest_returns_dict(self):
        """Manifest가 딕셔너리를 반환하는지 확인"""
        manifest = build_manifest()
        assert isinstance(manifest, dict)
    
    def test_manifest_has_required_fields(self):
        """Manifest에 필수 필드가 있는지 확인"""
        manifest = build_manifest()
        assert "aiw_version" in manifest
        assert "service" in manifest
        assert "endpoints" in manifest
        assert "schemas" in manifest
    
    def test_manifest_builder_chain(self):
        """ManifestBuilder 체이닝 테스트"""
        builder = ManifestBuilder()
        manifest = (
            builder
            .with_default_schemas()
            .with_default_endpoints()
            .with_default_auth()
            .build()
        )
        assert len(manifest["schemas"]) > 0
        assert len(manifest["endpoints"]) > 0


class TestDiffStream:
    """DiffStream 테스트"""
    
    def test_cursor_manager_initial(self):
        """초기 커서 확인"""
        cm = CursorManager()
        assert cm.get_cursor("any_subscriber") == CursorManager.INITIAL_CURSOR
    
    def test_cursor_manager_parse_format(self):
        """커서 파싱 및 포맷 테스트"""
        cm = CursorManager()
        cursor = cm.format_cursor(100)
        assert cursor == "cursor_000100"
        assert cm.parse_cursor(cursor) == 100
    
    def test_diff_engine_empty_events(self):
        """빈 이벤트 조회"""
        engine = DiffEngine()
        result = engine.get_events()
        assert result["since"] == CursorManager.INITIAL_CURSOR
        assert result["events"] == []
    
    def test_diff_engine_append_event(self):
        """이벤트 추가 테스트"""
        engine = DiffEngine()
        event = engine.append_event(
            event_type="TelemetryAppended",
            twin_id="twin_001",
            data_ref={"type": "telemetry", "id": "tel_001"},
        )
        assert event.event_type == "TelemetryAppended"
        assert event.twin_id == "twin_001"
        
        # 조회 확인
        result = engine.get_events()
        assert len(result["events"]) == 1


class TestSchemaRegistry:
    """SchemaRegistry 테스트"""
    
    def test_list_schemas(self):
        """스키마 목록 조회"""
        registry = SchemaRegistry()
        schemas = registry.list_schemas()
        assert len(schemas) > 0
        assert any(s["name"] == "telemetry.v1" for s in schemas)
    
    def test_get_builtin_schema(self):
        """내장 스키마 조회"""
        registry = SchemaRegistry()
        schema = registry.get_schema("telemetry.v1")
        assert schema is not None
        assert schema["$id"] == "telemetry.v1"
        assert "required" in schema
    
    def test_validate_valid_telemetry(self, sample_telemetry):
        """유효한 텔레메트리 검증"""
        registry = SchemaRegistry()
        data = {
            "event_id": "evt_001",
            "twin_id": sample_telemetry["twin_id"],
            "asset_id": sample_telemetry["asset_id"],
            "ts": "2026-01-04T12:00:00Z",
            "metrics": sample_telemetry["metrics"],
        }
        errors = registry.validate("telemetry.v1", data)
        assert errors == []
    
    def test_validate_invalid_telemetry(self):
        """유효하지 않은 텔레메트리 검증"""
        registry = SchemaRegistry()
        data = {"event_id": "evt_001"}  # 필수 필드 누락
        errors = registry.validate("telemetry.v1", data)
        assert len(errors) > 0


class TestSSEPublisher:
    """SSEPublisher 테스트"""
    
    def test_sse_message_format(self):
        """SSE 메시지 포맷 테스트"""
        msg = SSEMessage(
            event="test_event",
            data={"key": "value"},
            id="msg_001",
        )
        formatted = msg.format()
        assert "id: msg_001" in formatted
        assert "event: test_event" in formatted
        assert "data:" in formatted
    
    def test_publisher_subscriber_count(self):
        """구독자 수 확인"""
        publisher = SSEPublisher()
        assert publisher.subscriber_count == 0
