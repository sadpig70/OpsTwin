# -*- coding: utf-8 -*-
"""
Policy Module Unit Tests
========================
"""

import pytest
from src.opstwin.policy.permission_model import PermissionChecker, Permission, Role
from src.opstwin.policy.confidence_scorer import ConfidenceScorer, ConfidenceResult
from src.opstwin.policy.decision_maker import DecisionMaker, DecisionType


class TestPermissionChecker:
    """PermissionChecker 테스트"""
    
    def test_default_roles_exist(self):
        """기본 역할 존재 확인"""
        checker = PermissionChecker()
        assert "viewer" in checker._roles
        assert "admin" in checker._roles
        assert "agent" in checker._roles
    
    def test_assign_role(self):
        """역할 할당 테스트"""
        checker = PermissionChecker()
        result = checker.assign_role("user_001", "agent")
        assert result is True
        assert checker.check_permission("user_001", Permission.READ)
        assert checker.check_permission("user_001", Permission.PROPOSE)
    
    def test_admin_has_all_permissions(self, admin_user):
        """관리자 전체 권한 테스트"""
        checker = PermissionChecker()
        checker.assign_role(admin_user["user_id"], "admin")
        
        assert checker.check_permission(admin_user["user_id"], Permission.READ)
        assert checker.check_permission(admin_user["user_id"], Permission.PROPOSE)
        assert checker.check_permission(admin_user["user_id"], Permission.APPROVE)
        assert checker.check_permission(admin_user["user_id"], Permission.EXECUTE)
    
    def test_viewer_limited_permissions(self):
        """뷰어 제한된 권한 테스트"""
        checker = PermissionChecker()
        checker.assign_role("user_001", "viewer")
        
        assert checker.check_permission("user_001", Permission.READ)
        assert not checker.check_permission("user_001", Permission.PROPOSE)
        assert not checker.check_permission("user_001", Permission.EXECUTE)
    
    def test_audit_log_records(self):
        """감사 로그 기록 테스트"""
        checker = PermissionChecker()
        checker.assign_role("user_001", "viewer")
        checker.check_permission("user_001", Permission.READ)
        
        log = checker.get_audit_log()
        assert len(log) > 0
        assert log[-1]["user_id"] == "user_001"


class TestConfidenceScorer:
    """ConfidenceScorer 테스트"""
    
    def test_default_scores(self):
        """기본 점수 계산 테스트"""
        scorer = ConfidenceScorer()
        result = scorer.calculate(twin_id="twin_001")
        
        assert isinstance(result, ConfidenceResult)
        assert 0 <= result.total <= 1
        assert "historical_success_rate" in result.components
    
    def test_with_data_quality(self):
        """데이터 품질 포함 테스트"""
        scorer = ConfidenceScorer()
        result = scorer.calculate(
            twin_id="twin_001",
            data_quality=0.95,
        )
        
        assert result.components["data_quality_score"] == 0.95
    
    def test_with_simulation_result(self):
        """시뮬레이션 결과 포함 테스트"""
        scorer = ConfidenceScorer()
        result = scorer.calculate(
            twin_id="twin_001",
            simulation_result={
                "uncertainty": {"yield": 0.02},
            },
        )
        
        # 낮은 불확실성 → 높은 일관성
        assert result.components["simulation_consistency"] > 0.9
    
    def test_record_outcome(self):
        """결과 기록 테스트"""
        scorer = ConfidenceScorer()
        scorer.record_outcome(
            twin_id="twin_001",
            action_id="act_001",
            success=True,
            confidence_at_decision=0.85,
        )
        
        # 다음 계산에 반영
        result = scorer.calculate(twin_id="twin_001")
        assert result is not None


class TestDecisionMaker:
    """DecisionMaker 테스트"""
    
    def test_auto_execute_high_confidence(self):
        """높은 신뢰도 자동 실행"""
        maker = DecisionMaker()
        confidence = ConfidenceResult(
            total=0.95,
            components={},
            reasoning="High confidence",
        )
        
        decision = maker.decide(confidence)
        assert decision.decision_type == DecisionType.AUTO_EXECUTE
    
    def test_require_approval_medium_confidence(self):
        """중간 신뢰도 승인 필요"""
        maker = DecisionMaker()
        confidence = ConfidenceResult(
            total=0.80,
            components={},
            reasoning="Medium confidence",
        )
        
        decision = maker.decide(confidence)
        assert decision.decision_type == DecisionType.REQUIRE_APPROVAL
    
    def test_require_analysis_low_confidence(self):
        """낮은 신뢰도 분석 필요"""
        maker = DecisionMaker()
        confidence = ConfidenceResult(
            total=0.50,
            components={},
            reasoning="Low confidence",
        )
        
        decision = maker.decide(confidence)
        assert decision.decision_type == DecisionType.REQUIRE_ANALYSIS
    
    def test_safety_constraint_rejection(self):
        """안전 제약 위반 거부"""
        maker = DecisionMaker()
        maker.add_safety_constraint({
            "forbid": ["shutdown"],
            "reason": "Shutdown requires emergency flag",
        })
        
        confidence = ConfidenceResult(
            total=0.95,
            components={},
            reasoning="High confidence",
        )
        
        decision = maker.decide(
            confidence,
            proposed_action={"type": "shutdown"},
        )
        assert decision.decision_type == DecisionType.REJECT
        assert not decision.safety_check_passed
