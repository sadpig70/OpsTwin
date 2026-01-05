# -*- coding: utf-8 -*-
"""
Confidence Scorer Module
========================

신뢰도 점수 계산.
PPR 함수: AI_make_confidence_scorer() 기반 구현.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ConfidenceResult:
    """신뢰도 결과"""

    total: float  # 0.0 ~ 1.0
    components: Dict[str, float]
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "components": self.components,
            "reasoning": self.reasoning,
        }


class ConfidenceScorer:
    """신뢰도 점수기"""

    # 컴포넌트 가중치
    WEIGHTS = {
        "historical_success_rate": 0.25,
        "data_quality_score": 0.25,
        "simulation_consistency": 0.30,
        "ai_consensus_score": 0.20,
    }

    # 임계값
    THRESHOLDS = {
        "auto_execute": 0.90,
        "require_approval": 0.70,
    }

    def __init__(self):
        # 히스토리 저장 (twin_id별)
        self._history: Dict[str, List[Dict[str, Any]]] = {}

    def calculate(
        self,
        twin_id: str,
        data_quality: Optional[float] = None,
        simulation_result: Optional[Dict[str, Any]] = None,
        ai_agents: Optional[List[Dict[str, Any]]] = None,
    ) -> ConfidenceResult:
        """신뢰도 계산"""
        components: Dict[str, float] = {}
        reasoning_parts: List[str] = []

        # 1. Historical Success Rate
        historical = self._compute_historical_success(twin_id)
        components["historical_success_rate"] = historical
        reasoning_parts.append(f"Historical: {historical:.2f}")

        # 2. Data Quality Score
        if data_quality is not None:
            components["data_quality_score"] = data_quality
        else:
            components["data_quality_score"] = 0.8  # 기본값
        reasoning_parts.append(f"DataQuality: {components['data_quality_score']:.2f}")

        # 3. Simulation Consistency
        sim_consistency = self._compute_sim_consistency(simulation_result)
        components["simulation_consistency"] = sim_consistency
        reasoning_parts.append(f"SimConsistency: {sim_consistency:.2f}")

        # 4. AI Consensus Score
        ai_consensus = self._compute_ai_consensus(ai_agents)
        components["ai_consensus_score"] = ai_consensus
        reasoning_parts.append(f"AIConsensus: {ai_consensus:.2f}")

        # 가중 평균
        total = sum(components[key] * self.WEIGHTS[key] for key in self.WEIGHTS)

        return ConfidenceResult(
            total=round(total, 4),
            components=components,
            reasoning=" | ".join(reasoning_parts),
        )

    def _compute_historical_success(self, twin_id: str) -> float:
        """과거 성공률 계산"""
        history = self._history.get(twin_id, [])

        if len(history) < 10:
            return 0.5  # 데이터 부족 시 기본값

        successes = sum(1 for h in history if h.get("success", False))
        return successes / len(history)

    def _compute_sim_consistency(self, simulation_result: Optional[Dict[str, Any]]) -> float:
        """시뮬레이션 일관성 계산"""
        if not simulation_result:
            return 0.5  # 시뮬레이션 없음

        # 불확실성 기반 일관성
        uncertainty = simulation_result.get("uncertainty", {})
        if not uncertainty:
            return 0.8

        # 표준편차가 낮을수록 일관성 높음
        max_std = max(uncertainty.values()) if uncertainty else 0.1
        consistency = max(0, 1 - max_std)
        return round(consistency, 4)

    def _compute_ai_consensus(self, ai_agents: Optional[List[Dict[str, Any]]]) -> float:
        """AI 에이전트 합의 점수"""
        if not ai_agents or len(ai_agents) < 2:
            return 0.5  # 에이전트 부족

        # 추천 일치율
        recommendations = [a.get("recommendation") for a in ai_agents if a.get("recommendation")]
        if not recommendations:
            return 0.5

        from collections import Counter

        counter = Counter(recommendations)
        most_common_count = counter.most_common(1)[0][1]
        consensus = most_common_count / len(recommendations)
        return round(consensus, 4)

    def record_outcome(
        self,
        twin_id: str,
        action_id: str,
        success: bool,
        confidence_at_decision: float,
    ) -> None:
        """결과 기록 (학습용)"""
        if twin_id not in self._history:
            self._history[twin_id] = []

        self._history[twin_id].append(
            {
                "action_id": action_id,
                "success": success,
                "confidence": confidence_at_decision,
            }
        )

        # 최대 1000개 유지
        if len(self._history[twin_id]) > 1000:
            self._history[twin_id] = self._history[twin_id][-1000:]


# 싱글톤 인스턴스
confidence_scorer = ConfidenceScorer()
