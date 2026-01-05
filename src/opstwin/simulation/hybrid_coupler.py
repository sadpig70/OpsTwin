# -*- coding: utf-8 -*-
"""
Hybrid Coupler Module
=====================

고전-양자 하이브리드 결합기.
PPR 함수: AI_make_hybrid_coupler() 기반 구현.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import uuid4

from .monte_carlo import MonteCarloEngine, MonteCarloResult


class SimulationEngine(str, Enum):
    """시뮬레이션 엔진 유형"""

    CLASSICAL = "classical"
    QUANTUM = "quantum"
    HYBRID = "hybrid"


@dataclass
class SimulationInput:
    """시뮬레이션 입력"""

    twin_id: str
    scenario: str
    parameters: Dict[str, float]
    constraints: Dict[str, Any] = field(default_factory=dict)
    engine_preference: SimulationEngine = SimulationEngine.CLASSICAL
    n_samples: int = 1000


@dataclass
class SimulationOutput:
    """시뮬레이션 출력"""

    sim_id: str
    twin_id: str
    engine_used: SimulationEngine
    kpi_distribution: Dict[str, Dict[str, float]]
    recommended: Dict[str, Any]
    uncertainty: Dict[str, float]
    execution_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sim_id": self.sim_id,
            "twin_id": self.twin_id,
            "engine": self.engine_used.value,
            "kpi_distribution": self.kpi_distribution,
            "recommended": self.recommended,
            "uncertainty": self.uncertainty,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }


class HybridCoupler:
    """고전-양자 하이브리드 결합기"""

    # 양자 라우팅 임계값
    QUANTUM_THRESHOLD = {
        "problem_size_min": 10,
        "expected_speedup_min": 2.0,
    }

    def __init__(self):
        self.classical_engine = MonteCarloEngine()
        self._quantum_available = self._check_quantum_available()

    def _check_quantum_available(self) -> bool:
        """양자 백엔드 가용성 확인"""
        import importlib.util

        return importlib.util.find_spec("qiskit") is not None

    def run(self, sim_input: SimulationInput) -> SimulationOutput:
        """시뮬레이션 실행"""
        sim_id = f"sim_{uuid4().hex[:12]}"

        # 엔진 선택
        engine = self._select_engine(sim_input)

        # 시뮬레이션 실행
        if engine == SimulationEngine.QUANTUM and self._quantum_available:
            result = self._run_quantum(sim_input)
        else:
            result = self._run_classical(sim_input)

        # 결과 포맷
        kpi_distribution = {}
        uncertainty = {}

        for kpi_name, mc_result in result.items():
            kpi_distribution[kpi_name] = {
                "mean": round(mc_result.mean, 4),
                "std": round(mc_result.std, 4),
                "p5": mc_result.percentiles.get(5, 0),
                "p50": mc_result.percentiles.get(50, 0),
                "p95": mc_result.percentiles.get(95, 0),
            }
            uncertainty[kpi_name] = round(mc_result.std, 4)

        # 추천 생성
        recommended = self._generate_recommendation(kpi_distribution, uncertainty)

        # 총 실행 시간
        total_time = sum(r.execution_time_ms for r in result.values())

        return SimulationOutput(
            sim_id=sim_id,
            twin_id=sim_input.twin_id,
            engine_used=engine,
            kpi_distribution=kpi_distribution,
            recommended=recommended,
            uncertainty=uncertainty,
            execution_time_ms=round(total_time, 2),
        )

    def _select_engine(self, sim_input: SimulationInput) -> SimulationEngine:
        """엔진 선택 로직"""
        # 사용자 선호도 우선
        if sim_input.engine_preference != SimulationEngine.HYBRID:
            return sim_input.engine_preference

        # 양자 사용 불가
        if not self._quantum_available:
            return SimulationEngine.CLASSICAL

        # 문제 크기 기반 결정
        problem_size = len(sim_input.parameters)
        if problem_size >= self.QUANTUM_THRESHOLD["problem_size_min"]:
            return SimulationEngine.QUANTUM

        return SimulationEngine.CLASSICAL

    def _run_classical(
        self,
        sim_input: SimulationInput,
    ) -> Dict[str, MonteCarloResult]:
        """고전 시뮬레이션 실행"""
        return self.classical_engine.run_simple(
            scenario=sim_input.scenario,
            parameters=sim_input.parameters,
            n_samples=sim_input.n_samples,
        )

    def _run_quantum(
        self,
        sim_input: SimulationInput,
    ) -> Dict[str, MonteCarloResult]:
        """양자 시뮬레이션 실행 (MVP: 고전으로 폴백)"""
        # MVP: Qiskit 실제 연동은 Phase 2에서 구현
        # 현재는 고전으로 폴백하되 더 많은 샘플 사용
        return self.classical_engine.run_simple(
            scenario=sim_input.scenario,
            parameters=sim_input.parameters,
            n_samples=sim_input.n_samples * 2,  # 양자 대신 더 많은 샘플
        )

    def _generate_recommendation(
        self,
        kpi_distribution: Dict[str, Dict[str, float]],
        uncertainty: Dict[str, float],
    ) -> Dict[str, Any]:
        """추천 생성"""
        # 주요 KPI의 평균 성능
        avg_performance = sum(dist.get("mean", 0) for dist in kpi_distribution.values()) / max(
            len(kpi_distribution), 1
        )

        # 평균 불확실성
        avg_uncertainty = sum(uncertainty.values()) / max(len(uncertainty), 1)

        if avg_performance >= 0.9 and avg_uncertainty < 0.05:
            action = "proceed"
            confidence = 0.95
        elif avg_performance >= 0.8 and avg_uncertainty < 0.1:
            action = "proceed"
            confidence = 0.85
        elif avg_performance >= 0.7:
            action = "proceed_with_caution"
            confidence = 0.75
        else:
            action = "review_required"
            confidence = 0.5

        return {
            "action": action,
            "confidence": confidence,
            "reasoning": f"Avg performance: {avg_performance:.2%}, Avg uncertainty: {avg_uncertainty:.2%}",
        }


# 싱글톤 인스턴스
hybrid_coupler = HybridCoupler()
