# -*- coding: utf-8 -*-
"""
Simulation Module Unit Tests
============================
"""

import pytest
from src.opstwin.simulation.monte_carlo import MonteCarloEngine, MonteCarloResult
from src.opstwin.simulation.hybrid_coupler import HybridCoupler, SimulationEngine, SimulationInput


class TestMonteCarloEngine:
    """MonteCarloEngine 테스트"""
    
    def test_run_simple_returns_results(self):
        """간단한 시뮬레이션 결과 반환"""
        engine = MonteCarloEngine(n_samples=100, seed=42)
        results = engine.run_simple(
            scenario="test",
            parameters={"base_yield": 0.85},
        )
        
        assert "yield" in results
        assert isinstance(results["yield"], MonteCarloResult)
    
    def test_result_has_statistics(self):
        """결과에 통계 포함 확인"""
        engine = MonteCarloEngine(n_samples=100, seed=42)
        results = engine.run_simple(
            scenario="test",
            parameters={"base_yield": 0.85},
        )
        
        result = results["yield"]
        assert hasattr(result, "mean")
        assert hasattr(result, "std")
        assert hasattr(result, "percentiles")
        assert 50 in result.percentiles
    
    def test_custom_model_function(self):
        """커스텀 모델 함수 테스트"""
        engine = MonteCarloEngine(n_samples=100, seed=42)
        
        def custom_model(params):
            return {"output": params["input"] * 2}
        
        results = engine.run(
            model_fn=custom_model,
            parameter_distributions={
                "input": ("normal", {"mean": 5, "std": 1}),
            },
        )
        
        assert "output" in results
        assert results["output"].mean > 8  # 5 * 2 = 10 근처
    
    def test_convergence_check(self):
        """수렴 검사 테스트"""
        engine = MonteCarloEngine(n_samples=10000, seed=42)
        results = engine.run_simple(
            scenario="test",
            parameters={"base_yield": 0.85},
        )
        
        # 충분한 샘플로 수렴해야 함
        assert results["yield"].converged == True
    
    def test_different_distributions(self):
        """다양한 분포 테스트"""
        engine = MonteCarloEngine(n_samples=100, seed=42)
        
        def model(params):
            return {"sum": params["a"] + params["b"] + params["c"]}
        
        results = engine.run(
            model_fn=model,
            parameter_distributions={
                "a": ("normal", {"mean": 10, "std": 2}),
                "b": ("uniform", {"low": 0, "high": 5}),
                "c": ("triangular", {"left": 0, "mode": 2, "right": 5}),
            },
        )
        
        assert "sum" in results


class TestHybridCoupler:
    """HybridCoupler 테스트"""
    
    def test_classical_engine_default(self):
        """기본 고전 엔진 사용"""
        coupler = HybridCoupler()
        sim_input = SimulationInput(
            twin_id="twin_001",
            scenario="test",
            parameters={"base_yield": 0.85},
            engine_preference=SimulationEngine.CLASSICAL,
        )
        
        result = coupler.run(sim_input)
        assert result.engine_used == SimulationEngine.CLASSICAL
    
    def test_output_structure(self):
        """출력 구조 확인"""
        coupler = HybridCoupler()
        sim_input = SimulationInput(
            twin_id="twin_001",
            scenario="test",
            parameters={"base_yield": 0.85},
            n_samples=100,
        )
        
        result = coupler.run(sim_input)
        
        assert result.sim_id.startswith("sim_")
        assert result.twin_id == "twin_001"
        assert "yield" in result.kpi_distribution
        assert "action" in result.recommended
    
    def test_recommendation_generation(self):
        """추천 생성 테스트"""
        coupler = HybridCoupler()
        sim_input = SimulationInput(
            twin_id="twin_001",
            scenario="test",
            parameters={"base_yield": 0.90},  # 높은 성능
            n_samples=100,
        )
        
        result = coupler.run(sim_input)
        
        assert result.recommended["action"] in ["proceed", "proceed_with_caution", "review_required"]
        assert 0 <= result.recommended["confidence"] <= 1
    
    def test_uncertainty_included(self):
        """불확실성 포함 확인"""
        coupler = HybridCoupler()
        sim_input = SimulationInput(
            twin_id="twin_001",
            scenario="test",
            parameters={"base_yield": 0.85},
            n_samples=100,
        )
        
        result = coupler.run(sim_input)
        
        assert "yield" in result.uncertainty
        assert result.uncertainty["yield"] >= 0
