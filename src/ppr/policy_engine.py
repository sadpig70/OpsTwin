# -*- coding: utf-8 -*-
"""
Phase 0.3: Policy Engine PPR 함수 정의
======================================

정책 엔진 관련 PPR 함수 모음.
PermissionModel, PolicyEvaluator, ApprovalWorkflow, RollbackManager 4대 모듈의 16개 함수 정의.

Gantree Reference: OpsTwin_Gantree.md → PolicyEngine
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

# =============================================================================
# 데이터 타입 정의
# =============================================================================

class Permission(Enum):
    """권한 열거형 (RBAC)"""
    READ = "Read"
    PROPOSE = "Propose"
    APPROVE = "Approve"
    EXECUTE = "Execute"


class DecisionType(Enum):
    """정책 결정 유형"""
    AUTO_EXECUTE = "auto_execute"  # 신뢰도 >= 0.9
    REQUIRE_APPROVAL = "require_approval"  # 0.7 <= 신뢰도 < 0.9
    REQUIRE_ANALYSIS = "require_analysis"  # 신뢰도 < 0.7


@dataclass
class Role:
    """역할 정의"""
    name: str
    permissions: List[Permission]
    scope: Optional[str] = None  # twin_id 또는 asset_id


@dataclass
class ConfidenceScore:
    """신뢰도 점수 데이터"""
    total: float
    components: Dict[str, float]
    decision: DecisionType
    reasoning: str


# =============================================================================
# PermissionModel 함수 (PermissionModelFunction)
# =============================================================================

def AI_make_permission_model() -> Dict[str, Any]:
    """
    Gantree: PolicyEngine → PermissionModel
    
    Purpose:
        RBAC 기반 권한 모델 초기화.
    
    Inputs:
        없음
    
    Outputs:
        - model: Dict - 권한 모델 설정
    
    Dependencies:
        - AI_make_role_manager()
        - AI_make_permission_checker()
        - AI_make_audit_logger()
    
    Status: Design
    """
    return {
        "role_manager": AI_make_role_manager(),
        "permission_checker": AI_make_permission_checker(),
        "audit_logger": AI_make_audit_logger(),
        "enforcement_mode": "strict",  # strict | permissive | audit_only
        "status": "ready"
    }


def AI_make_role_manager() -> Dict[str, Any]:
    """
    Gantree: PermissionModel → RoleManager
    
    Purpose:
        역할 정의 및 할당 관리.
    
    Inputs:
        없음
    
    Outputs:
        - manager: Dict - 역할 관리자 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "default_roles": [
            {
                "name": "viewer",
                "permissions": [Permission.READ.value],
                "description": "읽기 전용 접근"
            },
            {
                "name": "agent",
                "permissions": [Permission.READ.value, Permission.PROPOSE.value],
                "description": "AI 에이전트 - 제안 가능"
            },
            {
                "name": "supervisor",
                "permissions": [Permission.READ.value, Permission.PROPOSE.value, Permission.APPROVE.value],
                "description": "감독자 - 승인 권한"
            },
            {
                "name": "executor",
                "permissions": [Permission.READ.value, Permission.EXECUTE.value],
                "description": "실행자 - 액션 실행 권한"
            },
            {
                "name": "admin",
                "permissions": [p.value for p in Permission],
                "description": "관리자 - 전체 권한"
            }
        ],
        "role_hierarchy": {
            "admin": ["supervisor", "executor"],
            "supervisor": ["agent", "viewer"],
            "executor": ["viewer"],
            "agent": ["viewer"]
        },
        "assignment_store": "database",  # database | ldap | oidc
        "status": "ready"
    }


def AI_make_permission_checker() -> Dict[str, Any]:
    """
    Gantree: PermissionModel → PermissionChecker
    
    Purpose:
        권한 검사기 설정. RBAC 기반 접근 제어.
    
    Inputs:
        없음
    
    Outputs:
        - checker: Dict - 권한 검사기 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "check_functions": {
            "read": {
                "required_permission": Permission.READ.value,
                "allow_if_no_policy": True
            },
            "propose": {
                "required_permission": Permission.PROPOSE.value,
                "allow_if_no_policy": False
            },
            "approve": {
                "required_permission": Permission.APPROVE.value,
                "allow_if_no_policy": False,
                "require_reason": True
            },
            "execute": {
                "required_permission": Permission.EXECUTE.value,
                "allow_if_no_policy": False,
                "require_idempotency_key": True
            }
        },
        "cache_ttl_seconds": 300,
        "fail_open": False,  # 검사 실패 시 거부
        "status": "ready"
    }


def AI_make_audit_logger() -> Dict[str, Any]:
    """
    Gantree: PermissionModel → AuditLogger
    
    Purpose:
        감사 로거 설정. 모든 권한 검사/액션 기록.
    
    Inputs:
        없음
    
    Outputs:
        - logger: Dict - 감사 로거 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "log_targets": [
            {"type": "database", "table": "audit_logs"},
            {"type": "kafka", "topic": "audit.events"},
            {"type": "file", "path": "/var/log/opstwin/audit.log"}
        ],
        "log_fields": [
            "timestamp", "actor_id", "actor_role", "action",
            "resource_type", "resource_id", "result", "reason", "ip_address"
        ],
        "retention_days": 365,
        "encryption": True,
        "status": "ready"
    }


# =============================================================================
# PolicyEvaluator 함수 (PolicyEvaluatorFunction)
# =============================================================================

def AI_make_policy_evaluator() -> Dict[str, Any]:
    """
    Gantree: PolicyEngine → PolicyEvaluator
    
    Purpose:
        정책 평가기 초기화. 조건 파싱, 신뢰도 계산, 결정 도출.
    
    Inputs:
        없음
    
    Outputs:
        - evaluator: Dict - 정책 평가기 설정
    
    Dependencies:
        - AI_make_condition_parser()
        - AI_make_confidence_scorer()
        - AI_make_decision_maker()
    
    Status: Design
    """
    return {
        "condition_parser": AI_make_condition_parser(),
        "confidence_scorer": AI_make_confidence_scorer(),
        "decision_maker": AI_make_decision_maker(),
        "evaluation_mode": "lazy",  # lazy | eager
        "cache_evaluations": True,
        "status": "ready"
    }


def AI_make_condition_parser() -> Dict[str, Any]:
    """
    Gantree: PolicyEvaluator → ConditionParser
    
    Purpose:
        조건 파서. 규칙 표현식 해석.
    
    Inputs:
        없음
    
    Outputs:
        - parser: Dict - 조건 파서 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "supported_operators": [
            "==", "!=", ">", ">=", "<", "<=",
            "in", "not_in", "contains", "matches",
            "and", "or", "not"
        ],
        "variable_sources": [
            "telemetry",   # 텔레메트리 메트릭
            "anomaly",     # 이상 탐지 결과
            "simulation",  # 시뮬레이션 결과
            "context"      # 컨텍스트 변수
        ],
        "expression_format": "simple",  # simple | cel | rego
        "max_complexity": 10,  # 중첩 깊이 제한
        "status": "ready"
    }


def AI_make_confidence_scorer() -> Dict[str, Any]:
    """
    Gantree: PolicyEvaluator → ConfidenceScorer
    
    Purpose:
        신뢰도 점수기. 4개 구성요소 가중 평균.
    
    Inputs:
        없음
    
    Outputs:
        - scorer: Dict - 신뢰도 점수기 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "components": {
            "historical_success_rate": {
                "weight": 0.25,
                "window_days": 30,
                "min_samples": 10,
                "default_if_insufficient": 0.5
            },
            "data_quality_score": {
                "weight": 0.25,
                "factors": ["completeness", "freshness", "consistency"],
                "threshold_min": 0.8
            },
            "simulation_consistency": {
                "weight": 0.30,
                "require_multiple_runs": True,
                "variance_threshold": 0.05
            },
            "ai_consensus_score": {
                "weight": 0.20,
                "min_agents": 2,
                "agreement_threshold": 0.75
            }
        },
        "aggregation_method": "weighted_average",
        "thresholds": {
            "auto_execute": 0.90,
            "require_approval": 0.70,
            "require_analysis": 0.0  # 기본값
        },
        "status": "ready"
    }


def AI_make_decision_maker() -> Dict[str, Any]:
    """
    Gantree: PolicyEvaluator → DecisionMaker
    
    Purpose:
        의사결정자. 신뢰도 기반 자동/승인/분석 분기.
    
    Inputs:
        없음
    
    Outputs:
        - decision_maker: Dict - 의사결정자 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "decision_rules": [
            {
                "condition": "confidence >= 0.90",
                "decision": DecisionType.AUTO_EXECUTE.value,
                "description": "자동 실행 - 높은 신뢰도"
            },
            {
                "condition": "confidence >= 0.70",
                "decision": DecisionType.REQUIRE_APPROVAL.value,
                "description": "승인 요청 - 중간 신뢰도"
            },
            {
                "condition": "confidence < 0.70",
                "decision": DecisionType.REQUIRE_ANALYSIS.value,
                "description": "추가 분석 필요 - 낮은 신뢰도"
            }
        ],
        "override_rules": [
            {
                "condition": "safety_constraint_violated",
                "decision": "reject",
                "description": "안전 제약 위반 시 자동 거부"
            }
        ],
        "fallback_decision": DecisionType.REQUIRE_ANALYSIS.value,
        "status": "ready"
    }


# =============================================================================
# ApprovalWorkflow 함수 (ApprovalWorkflowFunction)
# =============================================================================

def AI_make_approval_workflow() -> Dict[str, Any]:
    """
    Gantree: PolicyEngine → ApprovalWorkflow
    
    Purpose:
        승인 워크플로우 초기화.
    
    Inputs:
        없음
    
    Outputs:
        - workflow: Dict - 승인 워크플로우 설정
    
    Dependencies:
        - AI_make_proposal_generator()
        - AI_make_human_interface()
        - AI_make_feedback_processor()
    
    Status: Design
    """
    return {
        "proposal_generator": AI_make_proposal_generator(),
        "human_interface": AI_make_human_interface(),
        "feedback_processor": AI_make_feedback_processor(),
        "timeout_hours": 24,
        "escalation_rules": [
            {"after_hours": 4, "notify": "team_lead"},
            {"after_hours": 12, "notify": "manager"},
            {"after_hours": 24, "action": "auto_reject"}
        ],
        "status": "ready"
    }


def AI_make_proposal_generator() -> Dict[str, Any]:
    """
    Gantree: ApprovalWorkflow → ProposalGenerator
    
    Purpose:
        제안 생성기. 근거와 증거 포함 제안 패키지 생성.
    
    Inputs:
        없음
    
    Outputs:
        - generator: Dict - 제안 생성기 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "template": {
            "required_fields": [
                "proposal_id", "twin_id", "summary", "evidence",
                "expected_impact", "risk", "recommended_action"
            ],
            "optional_fields": [
                "alternatives", "rollback_plan", "time_sensitivity"
            ]
        },
        "reasoning_chain": {
            "include_causal_links": True,
            "max_chain_length": 5,
            "confidence_annotations": True
        },
        "evidence_collector": {
            "sources": ["telemetry", "anomaly", "simulation"],
            "max_evidence_items": 10,
            "include_visualizations": True
        },
        "status": "ready"
    }


def AI_make_human_interface() -> Dict[str, Any]:
    """
    Gantree: ApprovalWorkflow → HumanInterface
    
    Purpose:
        인간 인터페이스 설정. 대시보드/알림.
    
    Inputs:
        없음
    
    Outputs:
        - interface: Dict - 인간 인터페이스 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "dashboard": {
            "url_template": "/dashboard/proposals/{proposal_id}",
            "components": [
                "summary_card",
                "evidence_timeline",
                "impact_chart",
                "risk_matrix",
                "action_buttons"
            ]
        },
        "notification_channels": [
            {"type": "email", "priority": "all"},
            {"type": "slack", "priority": "high"},
            {"type": "sms", "priority": "critical"}
        ],
        "approval_methods": [
            "web_dashboard",
            "email_link",
            "slack_button",
            "api_call"
        ],
        "status": "ready"
    }


def AI_make_feedback_processor() -> Dict[str, Any]:
    """
    Gantree: ApprovalWorkflow → FeedbackProcessor
    
    Purpose:
        피드백 처리기. 승인/거부/수정 처리.
    
    Inputs:
        없음
    
    Outputs:
        - processor: Dict - 피드백 처리기 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "handlers": {
            "approved": {
                "next_action": "dispatch_to_executor",
                "require_signature": True,
                "log_level": "info"
            },
            "rejected": {
                "next_action": "notify_proposer",
                "require_reason": True,
                "log_level": "warning"
            },
            "modified": {
                "next_action": "regenerate_proposal",
                "apply_modifications": True,
                "log_level": "info"
            }
        },
        "learning_feedback": {
            "enabled": True,
            "update_confidence_model": True,
            "store_for_training": True
        },
        "status": "ready"
    }


# =============================================================================
# RollbackManager 함수 (RollbackManagerFunction)
# =============================================================================

def AI_make_rollback_manager() -> Dict[str, Any]:
    """
    Gantree: PolicyEngine → RollbackManager
    
    Purpose:
        롤백 관리자 초기화.
    
    Inputs:
        없음
    
    Outputs:
        - manager: Dict - 롤백 관리자 설정
    
    Dependencies:
        - AI_make_state_snapshot()
        - AI_make_rollback_executor()
        - AI_make_merkle_audit_log()
    
    Status: Design
    """
    return {
        "state_snapshot": AI_make_state_snapshot(),
        "rollback_executor": AI_make_rollback_executor(),
        "merkle_audit_log": AI_make_merkle_audit_log(),
        "auto_rollback_on_failure": True,
        "max_rollback_depth": 10,
        "status": "ready"
    }


def AI_make_state_snapshot() -> Dict[str, Any]:
    """
    Gantree: RollbackManager → StateSnapshot
    
    Purpose:
        상태 스냅샷 관리. 액션 실행 전 상태 저장.
    
    Inputs:
        없음
    
    Outputs:
        - snapshot: Dict - 상태 스냅샷 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "storage": {
            "type": "s3",
            "bucket": "opstwin-snapshots",
            "prefix": "state/",
            "compression": "zstd"
        },
        "capture_scope": [
            "asset_parameters",
            "configuration",
            "runtime_state"
        ],
        "retention_policy": {
            "keep_last_n": 100,
            "keep_days": 30,
            "keep_on_failure": True
        },
        "status": "ready"
    }


def AI_make_rollback_executor() -> Dict[str, Any]:
    """
    Gantree: RollbackManager → RollbackExecutor
    
    Purpose:
        롤백 실행기. 상태 복원 또는 보상 트랜잭션 실행.
    
    Inputs:
        없음
    
    Outputs:
        - executor: Dict - 롤백 실행기 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "strategies": {
            "snapshot_restore": {
                "description": "스냅샷에서 상태 복원",
                "applicable_when": "snapshot_available",
                "priority": 1
            },
            "compensation": {
                "description": "보상 트랜잭션 실행",
                "applicable_when": "compensation_defined",
                "priority": 2
            },
            "manual_intervention": {
                "description": "수동 개입 요청",
                "applicable_when": "auto_rollback_failed",
                "priority": 3
            }
        },
        "timeout_seconds": 300,
        "retry_attempts": 3,
        "notify_on_rollback": True,
        "status": "ready"
    }


def AI_make_merkle_audit_log() -> Dict[str, Any]:
    """
    Gantree: RollbackManager → MerkleAuditLog
    
    Purpose:
        Merkle 감사 로그. 위변조 탐지 가능한 감사 체인.
    
    Inputs:
        없음
    
    Outputs:
        - audit_log: Dict - Merkle 감사 로그 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "hash_algorithm": "sha256",
        "chain_structure": {
            "type": "merkle_tree",
            "branching_factor": 2,
            "leaf_size": 1000  # 리프당 이벤트 수
        },
        "verification": {
            "auto_verify_on_read": True,
            "verify_interval_minutes": 60,
            "alert_on_tampering": True
        },
        "anchoring": {
            "enabled": True,
            "target": "blockchain",  # blockchain | timestamping_service
            "interval_hours": 24
        },
        "status": "ready"
    }
