# -*- coding: utf-8 -*-
"""
Decision Maker Module
=====================

의사결정자.
PPR 함수: AI_make_decision_maker() 기반 구현.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .confidence_scorer import ConfidenceResult


class DecisionType(str, Enum):
    """결정 유형"""

    AUTO_EXECUTE = "auto_execute"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_ANALYSIS = "require_analysis"
    REJECT = "reject"


@dataclass
class Decision:
    """결정 결과"""

    decision_id: str
    decision_type: DecisionType
    confidence: float
    reasoning: str
    recommended_action: Optional[Dict[str, Any]] = None
    safety_check_passed: bool = True
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "recommended_action": self.recommended_action,
            "safety_check_passed": self.safety_check_passed,
            "timestamp": self.timestamp,
        }


class DecisionMaker:
    """의사결정자"""

    # 임계값
    THRESHOLDS = {
        "auto_execute": 0.90,
        "require_approval": 0.70,
    }

    def __init__(self):
        self._safety_constraints: List[Dict[str, Any]] = []
        self._decision_log: List[Decision] = []

    def add_safety_constraint(self, constraint: Dict[str, Any]) -> None:
        """안전 제약 추가"""
        self._safety_constraints.append(constraint)

    def decide(
        self,
        confidence_result: ConfidenceResult,
        proposed_action: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Decision:
        """의사결정 수행"""
        decision_id = f"dec_{uuid4().hex[:12]}"
        confidence = confidence_result.total

        # 안전 제약 검사
        safety_passed, safety_reason = self._check_safety_constraints(proposed_action, context)

        if not safety_passed:
            decision = Decision(
                decision_id=decision_id,
                decision_type=DecisionType.REJECT,
                confidence=confidence,
                reasoning=f"Safety constraint violation: {safety_reason}",
                recommended_action=None,
                safety_check_passed=False,
            )
        elif confidence >= self.THRESHOLDS["auto_execute"]:
            decision = Decision(
                decision_id=decision_id,
                decision_type=DecisionType.AUTO_EXECUTE,
                confidence=confidence,
                reasoning=f"High confidence ({confidence:.2%}) - auto execution approved",
                recommended_action=proposed_action,
                safety_check_passed=True,
            )
        elif confidence >= self.THRESHOLDS["require_approval"]:
            decision = Decision(
                decision_id=decision_id,
                decision_type=DecisionType.REQUIRE_APPROVAL,
                confidence=confidence,
                reasoning=f"Medium confidence ({confidence:.2%}) - human approval required",
                recommended_action=proposed_action,
                safety_check_passed=True,
            )
        else:
            decision = Decision(
                decision_id=decision_id,
                decision_type=DecisionType.REQUIRE_ANALYSIS,
                confidence=confidence,
                reasoning=f"Low confidence ({confidence:.2%}) - additional analysis needed",
                recommended_action=None,
                safety_check_passed=True,
            )

        self._decision_log.append(decision)
        return decision

    def _check_safety_constraints(
        self,
        action: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
    ) -> tuple[bool, str]:
        """안전 제약 검사"""
        if not action:
            return True, ""

        action_type = action.get("type", "")

        for constraint in self._safety_constraints:
            forbidden = constraint.get("forbid", [])
            if action_type in forbidden:
                return False, constraint.get("reason", f"Action type '{action_type}' is forbidden")

        # 기본 안전 검사
        if action_type == "shutdown" and not action.get("emergency", False):
            return False, "Non-emergency shutdown requires explicit emergency flag"

        return True, ""

    def get_decision_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """결정 로그 조회"""
        return [d.to_dict() for d in self._decision_log[-limit:]]


# 싱글톤 인스턴스
decision_maker = DecisionMaker()
