# -*- coding: utf-8 -*-
"""
Telemetry Module Unit Tests
===========================
"""

import pytest
from src.opstwin.telemetry.sensor_adapter import SensorConfig, MQTTSensorAdapter
from src.opstwin.telemetry.event_normalizer import EventNormalizer, normalize_telemetry
from src.opstwin.telemetry.anomaly_detector import AnomalyDetector, AnomalyKind


class TestSensorAdapter:
    """SensorAdapter 테스트"""
    
    @pytest.mark.asyncio
    async def test_mqtt_adapter_connect(self):
        """MQTT 어댑터 연결 테스트"""
        config = SensorConfig(
            sensor_id="sensor_001",
            sensor_type="mqtt",
            endpoint="mqtt://localhost:1883",
        )
        adapter = MQTTSensorAdapter(config)
        result = await adapter.connect()
        assert result is True
        assert adapter.is_connected is True
        await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_mqtt_adapter_read(self):
        """MQTT 어댑터 읽기 테스트"""
        config = SensorConfig(
            sensor_id="sensor_001",
            sensor_type="mqtt",
            endpoint="mqtt://localhost:1883",
        )
        adapter = MQTTSensorAdapter(config)
        await adapter.connect()
        reading = await adapter.read()
        
        assert reading is not None
        assert reading.sensor_id == "sensor_001"
        assert "temperature" in reading.metrics
        await adapter.disconnect()


class TestEventNormalizer:
    """EventNormalizer 테스트"""
    
    def test_normalize_basic(self, sample_telemetry):
        """기본 정규화 테스트"""
        normalizer = EventNormalizer()
        result = normalizer.normalize(
            raw_data={"metrics": sample_telemetry["metrics"]},
            twin_id=sample_telemetry["twin_id"],
            asset_id=sample_telemetry["asset_id"],
        )
        assert result.twin_id == sample_telemetry["twin_id"]
        assert "temperature" in result.metrics
    
    def test_normalize_unix_timestamp(self):
        """Unix 타임스탬프 정규화"""
        normalizer = EventNormalizer()
        result = normalizer.normalize(
            raw_data={
                "ts": 1704369600000,  # 밀리초
                "metrics": {"temp": 25.0},
            },
            twin_id="twin_001",
            asset_id="asset_001",
        )
        assert result.ts.endswith("Z")
        assert "2024" in result.ts or "2025" in result.ts or "2026" in result.ts
    
    def test_quality_computation(self):
        """품질 계산 테스트"""
        normalizer = EventNormalizer()
        result = normalizer.normalize(
            raw_data={
                "metrics": {"temp": 25.0},
                "expected_fields": ["temp", "humidity"],
            },
            twin_id="twin_001",
            asset_id="asset_001",
        )
        # humidity 누락 → completeness 0.5
        assert result.quality["data_quality_score"] == 0.5


class TestAnomalyDetector:
    """AnomalyDetector 테스트"""
    
    def test_no_anomaly_on_few_samples(self):
        """샘플 부족 시 이상 없음"""
        detector = AnomalyDetector()
        result = detector.detect(
            twin_id="twin_001",
            asset_id="asset_001",
            metrics={"temp": 25.0},
        )
        # 최소 10개 샘플 필요
        assert result is None
    
    def test_detects_spike(self):
        """스파이크 탐지 테스트"""
        detector = AnomalyDetector()
        
        # 정상 데이터 20개
        for _ in range(20):
            detector.detect(
                twin_id="twin_001",
                asset_id="asset_001",
                metrics={"temp": 25.0 + (0.1 * _)},  # 약간의 변동
            )
        
        # 스파이크 주입
        result = detector.detect(
            twin_id="twin_001",
            asset_id="asset_001",
            metrics={"temp": 100.0},  # 매우 높은 값
        )
        
        assert result is not None
        assert result.score > 0.5
        assert result.kind in [AnomalyKind.SPIKE, AnomalyKind.OUTLIER]
    
    def test_severity_levels(self):
        """심각도 레벨 테스트"""
        from src.opstwin.telemetry.anomaly_detector import Severity
        
        detector = AnomalyDetector()
        
        # 높은 점수 → 높은 심각도
        assert detector._determine_severity(0.96) == Severity.CRITICAL
        assert detector._determine_severity(0.88) == Severity.HIGH
        assert detector._determine_severity(0.75) == Severity.MEDIUM
        assert detector._determine_severity(0.55) == Severity.LOW
