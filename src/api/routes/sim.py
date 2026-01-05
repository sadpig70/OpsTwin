# -*- coding: utf-8 -*-
"""
Simulation Route
================

/sim/run 엔드포인트.
"""

from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/sim", tags=["Simulation"])


class SimulationRequest(BaseModel):
    """시뮬레이션 요청"""

    twin_id: str = Field(..., description="트윈 식별자")
    scenario: str = Field(..., description="시나리오 이름")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="시뮬레이션 파라미터")
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="제약 조건")
    n_samples: int = Field(default=1000, ge=100, le=100000, description="샘플 수")
    engine: str = Field(default="classical", description="엔진 (classical/quantum/hybrid)")


class SimulationResult(BaseModel):
    """시뮬레이션 결과"""

    sim_id: str
    engine: str
    status: str
    kpi_distribution: Dict[str, Dict[str, float]]
    recommended: Dict[str, Any]
    execution_time_ms: float


@router.post("/run", response_model=SimulationResult)
async def run_simulation(request: SimulationRequest):
    """시뮬레이션 실행"""
    import random
    import time

    start_time = time.time()

    # 시뮬레이션 ID 생성
    sim_id = f"sim_{uuid4().hex[:12]}"

    # MVP: 간단한 몬테카를로 시뮬레이션 (실제 구현은 Phase 1.4)
    samples = [random.gauss(0.85, 0.05) for _ in range(request.n_samples)]

    kpi_distribution = {
        "yield": {
            "mean": sum(samples) / len(samples),
            "std": (sum((x - sum(samples) / len(samples)) ** 2 for x in samples) / len(samples))
            ** 0.5,
            "p5": sorted(samples)[int(len(samples) * 0.05)],
            "p50": sorted(samples)[int(len(samples) * 0.50)],
            "p95": sorted(samples)[int(len(samples) * 0.95)],
        }
    }

    execution_time_ms = (time.time() - start_time) * 1000

    return SimulationResult(
        sim_id=sim_id,
        engine=request.engine,
        status="completed",
        kpi_distribution=kpi_distribution,
        recommended={"action": "proceed", "confidence": 0.85},
        execution_time_ms=round(execution_time_ms, 2),
    )
