# -*- coding: utf-8 -*-
"""
E2E Flow Integration Tests
==========================

전체 데이터 플로우 통합 테스트.
Telemetry → Anomaly → Policy → Simulation → Action 흐름 검증.
"""

import pytest
from src.opstwin.aiw.diff_stream import DiffEngine
from src.opstwin.aiw.schema_registry import SchemaRegistry
from src.opstwin.telemetry.event_normalizer import normalize_telemetry
from src.opstwin.telemetry.anomaly_detector import AnomalyDetector
from src.opstwin.policy.confidence_scorer import ConfidenceScorer
from src.opstwin.policy.decision_maker import DecisionMaker
from src.opstwin.simulation.hybrid_coupler import HybridCoupler, SimulationInput, SimulationEngine


class TestE2EHappyPath:
    """E2E 정상 흐름 테스트"""
    
    def test_telemetry_to_diff_event(self, sample_telemetry):
        """텔레메트리 → Diff 이벤트 플로우"""
        # 1. 정규화
        normalized = normalize_telemetry(
            sample_telemetry,
            sample_telemetry["twin_id"],
            sample_telemetry["asset_id"],
        )
        
        # 2. 스키마 검증
        registry = SchemaRegistry()
        errors = registry.validate("telemetry.v1", normalized)
        assert errors == []
        
        # 3. Diff 이벤트 추가
        engine = DiffEngine()
        event = engine.append_event(
            event_type="TelemetryAppended",
            twin_id=normalized["twin_id"],
            data_ref={"type": "telemetry", "id": normalized["event_id"]},
        )
        
        assert event.event_type == "TelemetryAppended"
    
    def test_anomaly_to_policy_decision(self):
        """이상 탐지 → 정책 결정 플로우"""
        # 1. 이상 탐지 (시뮬레이션)
        detector = AnomalyDetector()
        
        # 정상 데이터 학습
        for i in range(20):
            detector.detect("twin_001", "asset_001", {"temp": 25.0 + i * 0.1})
        
        # 이상 주입
        anomaly = detector.detect("twin_001", "asset_001", {"temp": 80.0})
        assert anomaly is not None
        
        # 2. 신뢰도 계산
        scorer = ConfidenceScorer()
        confidence = scorer.calculate(
            twin_id="twin_001",
            data_quality=0.9,
        )
        
        # 3. 의사결정
        maker = DecisionMaker()
        decision = maker.decide(confidence)
        
        assert decision.decision_type is not None
    
    def test_full_simulation_pipeline(self, sample_telemetry):
        """전체 시뮬레이션 파이프라인"""
        # 1. 텔레메트리 정규화
        normalized = normalize_telemetry(
            sample_telemetry,
            sample_telemetry["twin_id"],
            sample_telemetry["asset_id"],
        )
        
        # 2. 시뮬레이션 실행
        coupler = HybridCoupler()
        sim_input = SimulationInput(
            twin_id=normalized["twin_id"],
            scenario="optimization",
            parameters={
                "base_yield": 0.85,
                "temperature": normalized["metrics"]["temperature"],
            },
            n_samples=500,
        )
        
        result = coupler.run(sim_input)
        
        # 3. 신뢰도 계산 (시뮬레이션 결과 포함)
        scorer = ConfidenceScorer()
        confidence = scorer.calculate(
            twin_id=normalized["twin_id"],
            simulation_result={"uncertainty": result.uncertainty},
        )
        
        # 4. 의사결정
        maker = DecisionMaker()
        decision = maker.decide(
            confidence,
            proposed_action=result.recommended,
        )
        
        # 검증
        assert result.sim_id is not None
        assert confidence.total > 0
        assert decision.decision_id is not None


class TestE2EErrorHandling:
    """E2E 에러 처리 테스트"""
    
    def test_invalid_telemetry_rejected(self):
        """유효하지 않은 텔레메트리 거부"""
        registry = SchemaRegistry()
        
        invalid_data = {"event_id": "bad_001"}  # 필수 필드 누락
        errors = registry.validate("telemetry.v1", invalid_data)
        
        assert len(errors) > 0
    
    def test_safety_constraint_blocks_action(self):
        """안전 제약이 액션 차단"""
        from src.opstwin.policy.confidence_scorer import ConfidenceResult
        
        maker = DecisionMaker()
        maker.add_safety_constraint({
            "forbid": ["emergency_shutdown"],
            "reason": "Emergency shutdown requires manual override",
        })
        
        confidence = ConfidenceResult(
            total=0.99,
            components={},
            reasoning="Very high confidence",
        )
        
        decision = maker.decide(
            confidence,
            proposed_action={"type": "emergency_shutdown"},
        )
        
        assert decision.safety_check_passed is False
    
    def test_low_confidence_requires_analysis(self):
        """낮은 신뢰도 → 분석 필요"""
        from src.opstwin.policy.confidence_scorer import ConfidenceResult
        from src.opstwin.policy.decision_maker import DecisionType
        
        maker = DecisionMaker()
        confidence = ConfidenceResult(
            total=0.40,
            components={},
            reasoning="Low confidence",
        )
        
        decision = maker.decide(confidence)
        
        assert decision.decision_type == DecisionType.REQUIRE_ANALYSIS
