# -*- coding: utf-8 -*-
"""
Anomaly Detector Module
=======================

이상 탐지기.
PPR 함수: AI_make_anomaly_detector() 기반 구현.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

import numpy as np


class AnomalyKind(str, Enum):
    """이상 유형"""

    DRIFT = "drift"
    SPIKE = "spike"
    OUTLIER = "outlier"
    PATTERN = "pattern"
    MISSING = "missing"


class Severity(str, Enum):
    """심각도"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyResult:
    """이상 탐지 결과"""

    anomaly_id: str
    twin_id: str
    asset_id: str
    timestamp: str
    score: float  # 0.0 ~ 1.0
    kind: AnomalyKind
    severity: Severity
    features: Dict[str, float]
    recommended_next: str = "sim_run"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "anomaly_id": self.anomaly_id,
            "twin_id": self.twin_id,
            "asset_id": self.asset_id,
            "ts": self.timestamp,
            "score": self.score,
            "kind": self.kind.value,
            "severity": self.severity.value,
            "features": self.features,
            "recommended_next": self.recommended_next,
        }


class AnomalyDetector:
    """이상 탐지기"""

    # 심각도 임계값
    SEVERITY_THRESHOLDS = {
        Severity.CRITICAL: 0.95,
        Severity.HIGH: 0.85,
        Severity.MEDIUM: 0.70,
        Severity.LOW: 0.50,
    }

    def __init__(self):
        # 통계 저장 (자산별)
        self._stats: Dict[str, Dict[str, Dict[str, float]]] = {}
        # Z-Score 임계값
        self.zscore_threshold = 3.0
        # 최소 샘플 수
        self.min_samples = 10

    def detect(
        self,
        twin_id: str,
        asset_id: str,
        metrics: Dict[str, float],
        timestamp: Optional[str] = None,
    ) -> Optional[AnomalyResult]:
        """이상 탐지 수행"""
        key = f"{twin_id}:{asset_id}"

        # 통계 업데이트
        self._update_stats(key, metrics)

        # Z-Score 기반 이상 탐지
        scores = self._compute_zscores(key, metrics)

        if not scores:
            return None

        max_zscore = max(abs(s) for s in scores.values())

        # 이상 판정
        if max_zscore < self.zscore_threshold:
            return None

        # 이상 점수 계산 (0~1로 정규화)
        anomaly_score = min(1.0, max_zscore / 5.0)

        # 이상 유형 결정
        kind = self._determine_kind(scores, metrics)

        # 심각도 결정
        severity = self._determine_severity(anomaly_score)

        return AnomalyResult(
            anomaly_id=f"ano_{uuid4().hex[:12]}",
            twin_id=twin_id,
            asset_id=asset_id,
            timestamp=timestamp or (datetime.utcnow().isoformat() + "Z"),
            score=round(anomaly_score, 4),
            kind=kind,
            severity=severity,
            features=scores,
            recommended_next="sim_run"
            if severity in [Severity.HIGH, Severity.CRITICAL]
            else "monitor",
        )

    def _update_stats(self, key: str, metrics: Dict[str, float]) -> None:
        """통계 업데이트 (온라인 평균/분산)"""
        if key not in self._stats:
            self._stats[key] = {}

        for metric_name, value in metrics.items():
            if metric_name not in self._stats[key]:
                self._stats[key][metric_name] = {
                    "count": 0,
                    "mean": 0.0,
                    "m2": 0.0,
                }

            stats = self._stats[key][metric_name]
            stats["count"] += 1
            delta = value - stats["mean"]
            stats["mean"] += delta / stats["count"]
            delta2 = value - stats["mean"]
            stats["m2"] += delta * delta2

    def _compute_zscores(self, key: str, metrics: Dict[str, float]) -> Dict[str, float]:
        """Z-Score 계산"""
        if key not in self._stats:
            return {}

        scores = {}
        for metric_name, value in metrics.items():
            if metric_name not in self._stats[key]:
                continue

            stats = self._stats[key][metric_name]
            if stats["count"] < self.min_samples:
                continue

            variance = stats["m2"] / stats["count"]
            if variance < 1e-10:
                continue

            std = np.sqrt(variance)
            zscore = (value - stats["mean"]) / std
            scores[metric_name] = round(zscore, 4)

        return scores

    def _determine_kind(self, scores: Dict[str, float], metrics: Dict[str, float]) -> AnomalyKind:
        """이상 유형 결정"""
        max_field = max(scores, key=lambda k: abs(scores[k]))
        max_score = scores[max_field]

        if max_score > 4.0:
            return AnomalyKind.SPIKE
        elif max_score > 3.0:
            return AnomalyKind.OUTLIER
        else:
            return AnomalyKind.DRIFT

    def _determine_severity(self, score: float) -> Severity:
        """심각도 결정"""
        for severity, threshold in self.SEVERITY_THRESHOLDS.items():
            if score >= threshold:
                return severity
        return Severity.LOW


# 싱글톤 인스턴스
anomaly_detector = AnomalyDetector()
