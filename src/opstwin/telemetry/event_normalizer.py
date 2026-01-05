# -*- coding: utf-8 -*-
"""
Event Normalizer Module
=======================

이벤트 정규화기.
PPR 함수: AI_make_event_normalizer() 기반 구현.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from dateutil import parser as date_parser


@dataclass
class NormalizedTelemetry:
    """정규화된 텔레메트리 데이터"""

    event_id: str
    twin_id: str
    asset_id: str
    ts: str
    metrics: Dict[str, float]
    tags: Dict[str, str] = field(default_factory=dict)
    quality: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "event_id": self.event_id,
            "twin_id": self.twin_id,
            "asset_id": self.asset_id,
            "ts": self.ts,
            "metrics": self.metrics,
            "tags": self.tags,
            "quality": self.quality,
        }


class EventNormalizer:
    """이벤트 정규화기"""

    TIMESTAMP_FORMATS = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ]

    def __init__(self):
        self._field_mappings: Dict[str, str] = {}
        self._unit_conversions: Dict[str, callable] = {}

    def add_field_mapping(self, source: str, target: str) -> None:
        """필드 매핑 추가"""
        self._field_mappings[source] = target

    def add_unit_conversion(self, field: str, converter: callable) -> None:
        """단위 변환 추가"""
        self._unit_conversions[field] = converter

    def normalize(
        self,
        raw_data: Dict[str, Any],
        twin_id: str,
        asset_id: str,
    ) -> NormalizedTelemetry:
        """원시 데이터를 정규화된 텔레메트리로 변환"""
        # 이벤트 ID
        event_id = raw_data.get("event_id") or f"tel_{uuid4().hex[:12]}"

        # 타임스탬프 정규화
        ts = self._normalize_timestamp(raw_data.get("ts") or raw_data.get("timestamp"))

        # 메트릭 정규화
        metrics = self._normalize_metrics(raw_data.get("metrics", {}))

        # 태그 추출
        tags = raw_data.get("tags", {})
        if not isinstance(tags, dict):
            tags = {}

        # 품질 계산
        quality = self._compute_quality(metrics, raw_data)

        return NormalizedTelemetry(
            event_id=event_id,
            twin_id=twin_id,
            asset_id=asset_id,
            ts=ts,
            metrics=metrics,
            tags=tags,
            quality=quality,
        )

    def _normalize_timestamp(self, ts: Any) -> str:
        """타임스탬프 정규화 (RFC3339)"""
        if ts is None:
            return datetime.utcnow().isoformat() + "Z"

        if isinstance(ts, datetime):
            return ts.isoformat() + "Z"

        if isinstance(ts, (int, float)):
            # Unix timestamp (초 또는 밀리초)
            if ts > 1e12:  # 밀리초
                ts = ts / 1000
            return datetime.utcfromtimestamp(ts).isoformat() + "Z"

        if isinstance(ts, str):
            try:
                dt = date_parser.parse(ts)
                return dt.isoformat() + "Z"
            except Exception:
                return datetime.utcnow().isoformat() + "Z"

        return datetime.utcnow().isoformat() + "Z"

    def _normalize_metrics(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """메트릭 정규화"""
        normalized = {}
        for key, value in metrics.items():
            # 필드 매핑
            target_key = self._field_mappings.get(key, key)

            # 숫자로 변환
            try:
                float_value = float(value)
            except (TypeError, ValueError):
                continue

            # 단위 변환
            if target_key in self._unit_conversions:
                float_value = self._unit_conversions[target_key](float_value)

            normalized[target_key] = float_value

        return normalized

    def _compute_quality(
        self,
        metrics: Dict[str, float],
        raw_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """데이터 품질 계산"""
        expected_fields = raw_data.get("expected_fields", [])

        if not expected_fields:
            completeness = 1.0
        else:
            present = sum(1 for f in expected_fields if f in metrics)
            completeness = present / len(expected_fields)

        return {
            "data_quality_score": completeness,
            "missing_rate": 1.0 - completeness,
            "source": "normalized",
        }


def normalize_telemetry(
    raw_data: Dict[str, Any],
    twin_id: str,
    asset_id: str,
) -> Dict[str, Any]:
    """텔레메트리 데이터 정규화 (편의 함수)"""
    normalizer = EventNormalizer()
    normalized = normalizer.normalize(raw_data, twin_id, asset_id)
    return normalized.to_dict()
