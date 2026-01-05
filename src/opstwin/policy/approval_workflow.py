# -*- coding: utf-8 -*-
"""
Approval Workflow Module
========================

승인 워크플로우.
PPR 함수: AI_make_approval_workflow() 기반 구현.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4


class ProposalStatus(str, Enum):
    """제안 상태"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"


@dataclass
class Proposal:
    """제안"""

    proposal_id: str
    twin_id: str
    summary: str
    evidence: List[Dict[str, Any]]
    recommended_action: Dict[str, Any]
    confidence: float
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    expires_at: Optional[str] = None
    approved_by: Optional[str] = None
    approval_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "twin_id": self.twin_id,
            "summary": self.summary,
            "evidence": self.evidence,
            "recommended_action": self.recommended_action,
            "confidence": self.confidence,
            "status": self.status.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "approved_by": self.approved_by,
            "approval_reason": self.approval_reason,
        }


class ApprovalWorkflow:
    """승인 워크플로우 관리"""

    DEFAULT_TIMEOUT_HOURS = 24

    def __init__(self):
        self._proposals: Dict[str, Proposal] = {}
        self._on_approved: List[Callable[[Proposal], None]] = []
        self._on_rejected: List[Callable[[Proposal], None]] = []

    def create_proposal(
        self,
        twin_id: str,
        summary: str,
        evidence: List[Dict[str, Any]],
        recommended_action: Dict[str, Any],
        confidence: float,
        timeout_hours: int = DEFAULT_TIMEOUT_HOURS,
    ) -> Proposal:
        """제안 생성"""
        proposal_id = f"prop_{uuid4().hex[:12]}"
        expires = datetime.utcnow() + timedelta(hours=timeout_hours)

        proposal = Proposal(
            proposal_id=proposal_id,
            twin_id=twin_id,
            summary=summary,
            evidence=evidence,
            recommended_action=recommended_action,
            confidence=confidence,
            expires_at=expires.isoformat() + "Z",
        )

        self._proposals[proposal_id] = proposal
        return proposal

    def approve(
        self,
        proposal_id: str,
        approver_id: str,
        reason: Optional[str] = None,
    ) -> Optional[Proposal]:
        """제안 승인"""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return None

        if proposal.status != ProposalStatus.PENDING:
            return None

        proposal.status = ProposalStatus.APPROVED
        proposal.approved_by = approver_id
        proposal.approval_reason = reason or "Approved"

        # 콜백 호출
        for callback in self._on_approved:
            try:
                callback(proposal)
            except Exception:
                pass

        return proposal

    def reject(
        self,
        proposal_id: str,
        rejector_id: str,
        reason: str,
    ) -> Optional[Proposal]:
        """제안 거부"""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return None

        if proposal.status != ProposalStatus.PENDING:
            return None

        proposal.status = ProposalStatus.REJECTED
        proposal.approved_by = rejector_id
        proposal.approval_reason = reason

        # 콜백 호출
        for callback in self._on_rejected:
            try:
                callback(proposal)
            except Exception:
                pass

        return proposal

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """제안 조회"""
        return self._proposals.get(proposal_id)

    def list_pending(self, twin_id: Optional[str] = None) -> List[Proposal]:
        """대기 중인 제안 목록"""
        now = datetime.utcnow().isoformat() + "Z"

        pending = []
        for proposal in self._proposals.values():
            if proposal.status != ProposalStatus.PENDING:
                continue
            if twin_id and proposal.twin_id != twin_id:
                continue

            # 만료 검사
            if proposal.expires_at and proposal.expires_at < now:
                proposal.status = ProposalStatus.EXPIRED
                continue

            pending.append(proposal)

        return sorted(pending, key=lambda p: p.created_at, reverse=True)

    def on_approved(self, callback: Callable[[Proposal], None]) -> None:
        """승인 콜백 등록"""
        self._on_approved.append(callback)

    def on_rejected(self, callback: Callable[[Proposal], None]) -> None:
        """거부 콜백 등록"""
        self._on_rejected.append(callback)


# 싱글톤 인스턴스
approval_workflow = ApprovalWorkflow()
