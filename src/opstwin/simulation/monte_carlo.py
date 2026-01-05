# -*- coding: utf-8 -*-
"""
Monte Carlo Engine Module
=========================

몬테카를로 시뮬레이션 엔진.
PPR 함수: AI_make_monte_carlo_engine() 기반 구현.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class MonteCarloResult:
    """몬테카를로 시뮬레이션 결과"""

    kpi_name: str
    mean: float
    std: float
    percentiles: Dict[int, float]
    samples: int
    converged: bool
    execution_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kpi_name": self.kpi_name,
            "mean": self.mean,
            "std": self.std,
            "percentiles": {str(k): v for k, v in self.percentiles.items()},
            "samples": self.samples,
            "converged": self.converged,
            "execution_time_ms": self.execution_time_ms,
        }


class MonteCarloEngine:
    """몬테카를로 시뮬레이션 엔진"""

    DEFAULT_PERCENTILES = [5, 25, 50, 75, 95, 99]

    def __init__(
        self,
        n_samples: int = 10000,
        seed: Optional[int] = None,
        parallel_workers: int = 4,
    ):
        self.n_samples = n_samples
        self.seed = seed
        self.parallel_workers = parallel_workers

        if seed is not None:
            np.random.seed(seed)

    def run(
        self,
        model_fn: Callable[[Dict[str, float]], Dict[str, float]],
        parameter_distributions: Dict[str, Tuple[str, Dict[str, float]]],
        n_samples: Optional[int] = None,
    ) -> Dict[str, MonteCarloResult]:
        """몬테카를로 시뮬레이션 실행

        Args:
            model_fn: 모델 함수 (파라미터 → KPI)
            parameter_distributions: 파라미터 분포 정의
                {name: (distribution_type, params)}
                예: {"temp": ("normal", {"mean": 25, "std": 2})}
            n_samples: 샘플 수 (기본값: self.n_samples)

        Returns:
            KPI별 통계 결과
        """
        start_time = time.time()

        n = n_samples or self.n_samples

        # 파라미터 샘플 생성
        param_samples = self._generate_samples(parameter_distributions, n)

        # 모델 실행
        kpi_results: Dict[str, List[float]] = {}

        for i in range(n):
            params = {k: v[i] for k, v in param_samples.items()}
            try:
                kpis = model_fn(params)
                for kpi_name, value in kpis.items():
                    if kpi_name not in kpi_results:
                        kpi_results[kpi_name] = []
                    kpi_results[kpi_name].append(value)
            except Exception:
                continue  # 실패 시 스킵

        # 통계 계산
        execution_time = (time.time() - start_time) * 1000

        results = {}
        for kpi_name, values in kpi_results.items():
            arr = np.array(values)
            percentiles = {p: float(np.percentile(arr, p)) for p in self.DEFAULT_PERCENTILES}

            # 수렴 검사
            converged = self._check_convergence(arr)

            results[kpi_name] = MonteCarloResult(
                kpi_name=kpi_name,
                mean=float(np.mean(arr)),
                std=float(np.std(arr)),
                percentiles=percentiles,
                samples=len(arr),
                converged=converged,
                execution_time_ms=round(execution_time, 2),
            )

        return results

    def run_simple(
        self,
        scenario: str,
        parameters: Dict[str, float],
        n_samples: Optional[int] = None,
    ) -> Dict[str, MonteCarloResult]:
        """간단한 시뮬레이션 (내장 모델 사용)"""

        # 간단한 선형 모델 (MVP)
        def simple_model(params: Dict[str, float]) -> Dict[str, float]:
            noise = np.random.normal(0, 0.05)
            base_yield = params.get("base_yield", 0.85)
            temp_effect = (params.get("temperature", 25) - 25) * -0.01
            pressure_effect = (params.get("pressure", 1.0) - 1.0) * 0.02

            yield_value = base_yield + temp_effect + pressure_effect + noise
            return {
                "yield": np.clip(yield_value, 0, 1),
                "quality": np.clip(base_yield + noise, 0, 1),
            }

        # 파라미터 분포 생성
        distributions = {}
        for name, value in parameters.items():
            std = abs(value) * 0.1 if value != 0 else 0.1
            distributions[name] = ("normal", {"mean": value, "std": std})

        return self.run(simple_model, distributions, n_samples)

    def _generate_samples(
        self,
        distributions: Dict[str, Tuple[str, Dict[str, float]]],
        n: int,
    ) -> Dict[str, np.ndarray]:
        """파라미터 샘플 생성"""
        samples = {}

        for name, (dist_type, params) in distributions.items():
            if dist_type == "normal":
                samples[name] = np.random.normal(params.get("mean", 0), params.get("std", 1), n)
            elif dist_type == "uniform":
                samples[name] = np.random.uniform(params.get("low", 0), params.get("high", 1), n)
            elif dist_type == "triangular":
                samples[name] = np.random.triangular(
                    params.get("left", 0), params.get("mode", 0.5), params.get("right", 1), n
                )
            elif dist_type == "lognormal":
                samples[name] = np.random.lognormal(
                    params.get("mean", 0), params.get("sigma", 1), n
                )
            else:
                # 기본: 상수
                samples[name] = np.full(n, params.get("value", 0))

        return samples

    def _check_convergence(
        self,
        values: np.ndarray,
        tolerance: float = 0.01,
        min_samples: int = 1000,
    ) -> bool:
        """수렴 검사 (표준오차 기반)"""
        if len(values) < min_samples:
            return False

        # 표준오차
        se = np.std(values) / np.sqrt(len(values))
        mean = np.mean(values)

        if mean == 0:
            return se < tolerance

        # 상대 표준오차
        relative_se = se / abs(mean)
        return relative_se < tolerance


# 싱글톤 인스턴스
monte_carlo_engine = MonteCarloEngine()
