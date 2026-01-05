# -*- coding: utf-8 -*-
"""
Phase 0.2: Telemetry Layer PPR 함수 정의
========================================

텔레메트리 레이어 관련 PPR 함수 모음.
DataCollector, StreamProcessor, TimeSeriesDB 3대 모듈의 11개 함수 정의.

Gantree Reference: OpsTwin_Gantree.md → TelemetryLayer
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

# =============================================================================
# 데이터 타입 정의
# =============================================================================

class AnomalyKind(Enum):
    """이상 유형 열거형"""
    DRIFT = "drift"           # 드리프트
    SPIKE = "spike"           # 급등
    OUTLIER = "outlier"       # 이상치
    PATTERN = "pattern"       # 패턴 이상
    MISSING = "missing"       # 결측


@dataclass
class SensorConfig:
    """센서 어댑터 설정"""
    sensor_id: str
    sensor_type: str  # plc, opc-ua, mqtt, modbus
    endpoint: str
    polling_interval_ms: int = 1000
    timeout_ms: int = 5000


@dataclass
class TelemetryEvent:
    """텔레메트리 이벤트 데이터"""
    event_id: str
    twin_id: str
    asset_id: str
    timestamp: str
    metrics: Dict[str, float]
    tags: Dict[str, str] = field(default_factory=dict)
    quality: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyEvent:
    """이상 탐지 이벤트 데이터"""
    anomaly_id: str
    twin_id: str
    asset_id: str
    timestamp: str
    score: float
    kind: AnomalyKind
    features: Dict[str, float]
    recommended_next: str = "sim_run"


# =============================================================================
# DataCollector 함수 (DataCollectorFunction)
# =============================================================================

def AI_make_data_collector(sensors: List[SensorConfig] = None) -> Dict[str, Any]:
    """
    Gantree: TelemetryLayer → DataCollector
    
    Purpose:
        센서/로그 데이터 수집기 초기화. 다중 센서 통합 관리.
    
    Inputs:
        - sensors: List[SensorConfig] - 센서 설정 목록 (선택)
    
    Outputs:
        - collector: Dict - 데이터 수집기 설정 및 상태
    
    Dependencies:
        - AI_make_sensor_adapter()
        - AI_make_log_ingester()
        - AI_make_metric_aggregator()
    
    Status: Design
    """
    if sensors is None:
        sensors = []

    return {
        "status": "initialized",
        "sensors": [AI_make_sensor_adapter(s) for s in sensors],
        "log_ingester": AI_make_log_ingester(),
        "metric_aggregator": AI_make_metric_aggregator(),
        "collection_mode": "streaming",
        "buffer_size": 10000
    }


def AI_make_sensor_adapter(config: SensorConfig = None) -> Dict[str, Any]:
    """
    Gantree: DataCollector → SensorAdapter
    
    Purpose:
        센서 어댑터 인터페이스 생성. 다양한 프로토콜 지원.
    
    Inputs:
        - config: SensorConfig - 센서 설정
    
    Outputs:
        - adapter: Dict - 센서 어댑터 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    if config is None:
        config = SensorConfig(
            sensor_id="default_sensor",
            sensor_type="mqtt",
            endpoint="mqtt://localhost:1883"
        )

    # 프로토콜별 어댑터 매핑
    protocol_adapters = {
        "plc": {"driver": "pylogix", "format": "raw"},
        "opc-ua": {"driver": "asyncua", "format": "opc"},
        "mqtt": {"driver": "paho-mqtt", "format": "json"},
        "modbus": {"driver": "pymodbus", "format": "register"}
    }

    adapter_config = protocol_adapters.get(config.sensor_type, protocol_adapters["mqtt"])

    return {
        "sensor_id": config.sensor_id,
        "sensor_type": config.sensor_type,
        "endpoint": config.endpoint,
        "polling_interval_ms": config.polling_interval_ms,
        "timeout_ms": config.timeout_ms,
        "driver": adapter_config["driver"],
        "format": adapter_config["format"],
        "status": "ready"
    }


def AI_make_log_ingester() -> Dict[str, Any]:
    """
    Gantree: DataCollector → LogIngester
    
    Purpose:
        로그 수집기 설정. 다양한 로그 소스 통합.
    
    Inputs:
        없음
    
    Outputs:
        - ingester: Dict - 로그 수집기 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "sources": [
            {"type": "file", "path": "/var/log/*.log", "parser": "regex"},
            {"type": "syslog", "port": 514, "parser": "syslog"},
            {"type": "journald", "unit": "*", "parser": "journald"}
        ],
        "buffer_lines": 10000,
        "flush_interval_ms": 1000,
        "timestamp_format": "RFC3339",
        "status": "ready"
    }


def AI_make_metric_aggregator() -> Dict[str, Any]:
    """
    Gantree: DataCollector → MetricAggregator
    
    Purpose:
        메트릭 집계기 설정. 시간 윈도우별 집계 지원.
    
    Inputs:
        없음
    
    Outputs:
        - aggregator: Dict - 메트릭 집계기 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "windows": [
            {"duration_sec": 1, "functions": ["mean", "last"]},
            {"duration_sec": 60, "functions": ["mean", "min", "max", "stddev"]},
            {"duration_sec": 3600, "functions": ["mean", "p50", "p95", "p99"]}
        ],
        "output_format": "telemetry.v1",
        "emit_on": "window_close",
        "status": "ready"
    }


# =============================================================================
# StreamProcessor 함수 (StreamProcessorFunction)
# =============================================================================

def AI_make_stream_processor() -> Dict[str, Any]:
    """
    Gantree: TelemetryLayer → StreamProcessor
    
    Purpose:
        스트림 처리 엔진 초기화. Kafka 기반 이벤트 처리.
    
    Inputs:
        없음
    
    Outputs:
        - processor: Dict - 스트림 프로세서 설정
    
    Dependencies:
        - AI_make_kafka_connector()
        - AI_make_event_normalizer()
        - AI_make_anomaly_detector()
    
    Status: Design
    """
    return {
        "kafka": AI_make_kafka_connector(),
        "normalizer": AI_make_event_normalizer(),
        "anomaly_detector": AI_make_anomaly_detector(),
        "parallelism": 4,
        "checkpoint_interval_ms": 10000,
        "status": "ready"
    }


def AI_make_kafka_connector(bootstrap_servers: str = "localhost:9092") -> Dict[str, Any]:
    """
    Gantree: StreamProcessor → KafkaConnector
    
    Purpose:
        Kafka 연동 커넥터 설정.
    
    Inputs:
        - bootstrap_servers: str - Kafka 브로커 주소
    
    Outputs:
        - connector: Dict - Kafka 커넥터 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "bootstrap_servers": bootstrap_servers,
        "topics": {
            "input": "telemetry.raw",
            "output": "telemetry.normalized",
            "anomaly": "anomaly.detected",
            "dlq": "telemetry.dlq"  # Dead Letter Queue
        },
        "consumer_group": "opstwin-processor",
        "auto_offset_reset": "latest",
        "enable_auto_commit": False,
        "max_poll_records": 500,
        "status": "ready"
    }


def AI_make_event_normalizer() -> Dict[str, Any]:
    """
    Gantree: StreamProcessor → EventNormalizer
    
    Purpose:
        이벤트 정규화기. 다양한 포맷을 telemetry.v1으로 변환.
    
    Inputs:
        없음
    
    Outputs:
        - normalizer: Dict - 정규화 규칙 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "input_formats": ["json", "avro", "protobuf", "csv"],
        "output_format": "telemetry.v1",
        "transformations": [
            {"type": "timestamp_parse", "formats": ["RFC3339", "unix_ms", "iso8601"]},
            {"type": "field_rename", "mapping": {}},  # 동적 설정
            {"type": "unit_convert", "rules": []},    # 단위 변환 규칙
            {"type": "quality_compute", "method": "completeness_check"}
        ],
        "drop_invalid": False,
        "route_invalid_to_dlq": True,
        "status": "ready"
    }


def AI_make_anomaly_detector() -> Dict[str, Any]:
    """
    Gantree: StreamProcessor → AnomalyDetector
    
    Purpose:
        이상 탐지기 초기화. 다중 탐지 모델 지원.
    
    Inputs:
        없음
    
    Outputs:
        - detector: Dict - 이상 탐지기 설정
    
    Dependencies:
        - FeatureExtractor (내부)
        - DetectionModel (내부)
        - AlertDispatcher (내부)
    
    Status: Design
    """
    return {
        "feature_extractor": {
            "statistical_features": ["mean", "std", "zscore", "ema"],
            "temporal_patterns": ["trend", "seasonality", "change_point"],
            "window_sizes": [60, 300, 3600]  # 1분, 5분, 1시간
        },
        "detection_models": [
            {
                "name": "isolation_forest",
                "type": "IsolationForest",
                "contamination": 0.01,
                "enabled": True
            },
            {
                "name": "zscore_detector",
                "type": "ZScore",
                "threshold": 3.0,
                "enabled": True
            },
            {
                "name": "threshold_alerts",
                "type": "Threshold",
                "rules": [],  # 동적 설정
                "enabled": True
            }
        ],
        "alert_dispatcher": {
            "severity_thresholds": {
                "critical": 0.95,
                "high": 0.85,
                "medium": 0.70,
                "low": 0.50
            },
            "channels": ["kafka", "webhook"],
            "rate_limit_per_asset": 10  # 자산당 분당 최대 알림
        },
        "ensemble_method": "max_score",
        "output_topic": "anomaly.detected",
        "status": "ready"
    }


# =============================================================================
# TimeSeriesDB 함수 (TimeSeriesDBFunction)
# =============================================================================

def AI_make_timeseries_db() -> Dict[str, Any]:
    """
    Gantree: TelemetryLayer → TimeSeriesDB
    
    Purpose:
        시계열 데이터베이스 설정 초기화.
    
    Inputs:
        없음
    
    Outputs:
        - db_config: Dict - TimescaleDB 설정
    
    Dependencies:
        - AI_make_timescale_adapter()
        - AI_make_retention_manager()
    
    Status: Design
    """
    return {
        "adapter": AI_make_timescale_adapter(),
        "retention": AI_make_retention_manager(),
        "compression": {
            "enabled": True,
            "after_days": 7,
            "segment_by": "twin_id"
        },
        "status": "ready"
    }


def AI_make_timescale_adapter(connection_string: str = None) -> Dict[str, Any]:
    """
    Gantree: TimeSeriesDB → TimescaleAdapter
    
    Purpose:
        TimescaleDB 어댑터 설정.
    
    Inputs:
        - connection_string: str - DB 연결 문자열 (선택)
    
    Outputs:
        - adapter: Dict - TimescaleDB 어댑터 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    if connection_string is None:
        connection_string = "postgresql://opstwin:password@localhost:5432/opstwin"

    return {
        "connection_string": connection_string,
        "hypertable": {
            "table_name": "telemetry_events",
            "time_column": "ts",
            "chunk_interval": "1 day",
            "partitioning_column": "twin_id"
        },
        "pool": {
            "min_connections": 5,
            "max_connections": 20,
            "connection_timeout_ms": 5000
        },
        "batch_insert": {
            "enabled": True,
            "batch_size": 1000,
            "flush_interval_ms": 100
        },
        "status": "ready"
    }


def AI_make_retention_manager() -> Dict[str, Any]:
    """
    Gantree: TimeSeriesDB → RetentionManager
    
    Purpose:
        데이터 보존 관리자 설정. TTL 기반 자동 삭제.
    
    Inputs:
        없음
    
    Outputs:
        - retention: Dict - 보존 정책 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "policies": [
            {
                "name": "raw_telemetry",
                "table": "telemetry_events",
                "retention_days": 30,
                "action": "drop_chunks"
            },
            {
                "name": "aggregated_1min",
                "table": "telemetry_1min",
                "retention_days": 90,
                "action": "drop_chunks"
            },
            {
                "name": "aggregated_1hour",
                "table": "telemetry_1hour",
                "retention_days": 365,
                "action": "drop_chunks"
            },
            {
                "name": "anomaly_events",
                "table": "anomaly_events",
                "retention_days": 365,
                "action": "archive_to_s3"
            }
        ],
        "schedule": "0 2 * * *",  # 매일 02:00 실행
        "dry_run": False,
        "status": "ready"
    }
