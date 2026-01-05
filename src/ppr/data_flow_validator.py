# -*- coding: utf-8 -*-
"""
Phase 0.5: Data Flow Validator PPR 함수 정의
============================================

데이터 플로우 검증 관련 PPR 함수 모음.
InterfaceContract, FlowSimulator, ValidationReport 3대 모듈의 12개 함수 정의.

Gantree Reference: OpsTwin_PPR_Definition_Plan.md → Phase0_5_DataFlow_Validation
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

# =============================================================================
# 데이터 타입 정의
# =============================================================================

class FlowStatus(Enum):
    """플로우 상태"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ContractType(Enum):
    """계약 유형"""
    REQUEST_RESPONSE = "request_response"
    EVENT_STREAM = "event_stream"
    PUBLISH_SUBSCRIBE = "publish_subscribe"


@dataclass
class InterfaceEndpoint:
    """인터페이스 엔드포인트 정의"""
    name: str
    input_schema: str
    output_schema: str
    contract_type: ContractType


@dataclass
class FlowTestResult:
    """플로우 테스트 결과"""
    test_name: str
    status: FlowStatus
    duration_ms: float
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str] = None


# =============================================================================
# InterfaceContract 함수 (InterfaceContractFunction)
# =============================================================================

def AI_make_interface_contract() -> Dict[str, Any]:
    """
    Gantree: Phase0_5_DataFlow_Validation → InterfaceContract
    
    Purpose:
        인터페이스 계약 정의. 모듈 간 데이터 교환 규약.
    
    Inputs:
        없음
    
    Outputs:
        - contracts: Dict - 전체 인터페이스 계약 모음
    
    Dependencies:
        - AI_make_aiw_telemetry_contract()
        - AI_make_telemetry_policy_contract()
        - AI_make_policy_simulation_contract()
        - AI_make_simulation_action_contract()
    
    Status: Design
    """
    return {
        "contracts": {
            "aiw_telemetry": AI_make_aiw_telemetry_contract(),
            "telemetry_policy": AI_make_telemetry_policy_contract(),
            "policy_simulation": AI_make_policy_simulation_contract(),
            "simulation_action": AI_make_simulation_action_contract()
        },
        "validation_mode": "strict",
        "schema_validation": True,
        "status": "ready"
    }


def AI_make_aiw_telemetry_contract() -> Dict[str, Any]:
    """
    Gantree: InterfaceContract → AIW_Telemetry_Contract
    
    Purpose:
        AIW Protocol ↔ Telemetry Layer 인터페이스 계약.
    
    Inputs:
        없음
    
    Outputs:
        - contract: Dict - AIW-Telemetry 계약 명세
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "name": "AIW ↔ Telemetry",
        "endpoints": [
            {
                "direction": "telemetry → aiw",
                "event_type": "TelemetryAppended",
                "input_schema": "telemetry.v1",
                "output_schema": "diff_event.v1",
                "trigger": "on_telemetry_store"
            },
            {
                "direction": "telemetry → aiw",
                "event_type": "AnomalyDetected",
                "input_schema": "anomaly.v1",
                "output_schema": "diff_event.v1",
                "trigger": "on_anomaly_detect"
            }
        ],
        "data_flow": {
            "source_module": "TelemetryLayer",
            "target_module": "AIW_Protocol",
            "protocol": "event_stream",
            "serialization": "json"
        },
        "guarantees": {
            "ordering": "causal",
            "delivery": "at_least_once",
            "latency_p99_ms": 100
        }
    }


def AI_make_telemetry_policy_contract() -> Dict[str, Any]:
    """
    Gantree: InterfaceContract → Telemetry_Policy_Contract
    
    Purpose:
        Telemetry Layer ↔ Policy Engine 인터페이스 계약.
    
    Inputs:
        없음
    
    Outputs:
        - contract: Dict - Telemetry-Policy 계약 명세
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "name": "Telemetry ↔ Policy",
        "endpoints": [
            {
                "direction": "telemetry → policy",
                "event_type": "AnomalyDetected",
                "input_schema": "anomaly.v1",
                "output_schema": "policy_decision.v1",
                "trigger": "on_anomaly_score_threshold"
            },
            {
                "direction": "telemetry → policy",
                "event_type": "DataQualityReport",
                "input_schema": "quality_metrics.v1",
                "output_schema": "confidence_update.v1",
                "trigger": "periodic_1min"
            }
        ],
        "data_flow": {
            "source_module": "TelemetryLayer.AnomalyDetector",
            "target_module": "PolicyEngine.ConfidenceScorer",
            "protocol": "request_response",
            "serialization": "json"
        },
        "guarantees": {
            "ordering": "fifo",
            "delivery": "exactly_once",
            "latency_p99_ms": 50
        }
    }


def AI_make_policy_simulation_contract() -> Dict[str, Any]:
    """
    Gantree: InterfaceContract → Policy_Simulation_Contract
    
    Purpose:
        Policy Engine ↔ Simulation Engine 인터페이스 계약.
    
    Inputs:
        없음
    
    Outputs:
        - contract: Dict - Policy-Simulation 계약 명세
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "name": "Policy ↔ Simulation",
        "endpoints": [
            {
                "direction": "policy → simulation",
                "request_type": "SimulationRequest",
                "input_schema": "sim_input.v1",
                "output_schema": "sim_result.v1",
                "trigger": "on_analysis_required"
            },
            {
                "direction": "simulation → policy",
                "event_type": "SimulationCompleted",
                "input_schema": "sim_result.v1",
                "output_schema": "confidence_update.v1",
                "trigger": "on_sim_complete"
            }
        ],
        "data_flow": {
            "source_module": "PolicyEngine.DecisionMaker",
            "target_module": "SimulationEngine.HybridCoupler",
            "protocol": "request_response",
            "serialization": "json",
            "async_mode": True
        },
        "guarantees": {
            "ordering": "none",
            "delivery": "at_least_once",
            "timeout_ms": 30000,
            "retry_policy": {
                "max_retries": 3,
                "backoff": "exponential"
            }
        }
    }


def AI_make_simulation_action_contract() -> Dict[str, Any]:
    """
    Gantree: InterfaceContract → Simulation_Action_Contract
    
    Purpose:
        Simulation Engine ↔ Action Executor 인터페이스 계약.
    
    Inputs:
        없음
    
    Outputs:
        - contract: Dict - Simulation-Action 계약 명세
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "name": "Simulation ↔ Action",
        "endpoints": [
            {
                "direction": "policy → action",
                "request_type": "ActionDispatch",
                "input_schema": "action.v1",
                "output_schema": "action_result.v1",
                "trigger": "on_decision_auto_execute"
            },
            {
                "direction": "action → policy",
                "event_type": "ActionSucceeded",
                "input_schema": "action_result.v1",
                "output_schema": "audit_log.v1",
                "trigger": "on_action_complete"
            },
            {
                "direction": "action → policy",
                "event_type": "ActionFailed",
                "input_schema": "action_error.v1",
                "output_schema": "rollback_trigger.v1",
                "trigger": "on_action_failure"
            }
        ],
        "data_flow": {
            "source_module": "PolicyEngine.ApprovalWorkflow",
            "target_module": "ActionExecutor.CommandDispatcher",
            "protocol": "request_response",
            "serialization": "json",
            "async_mode": True
        },
        "guarantees": {
            "ordering": "strict",
            "delivery": "exactly_once",
            "idempotency": "required",
            "timeout_ms": 60000
        }
    }


# =============================================================================
# FlowSimulator 함수 (FlowSimulatorFunction)
# =============================================================================

def AI_make_flow_simulator() -> Dict[str, Any]:
    """
    Gantree: Phase0_5_DataFlow_Validation → FlowSimulator
    
    Purpose:
        플로우 시뮬레이터 초기화. 데이터 플로우 테스트.
    
    Inputs:
        없음
    
    Outputs:
        - simulator: Dict - 플로우 시뮬레이터 설정
    
    Dependencies:
        - AI_make_l0_l1_flow_test()
        - AI_make_l1_l2_flow_test()
        - AI_make_e2e_flow_test()
    
    Status: Design
    """
    return {
        "tests": {
            "l0_l1": AI_make_l0_l1_flow_test(),
            "l1_l2": AI_make_l1_l2_flow_test(),
            "e2e": AI_make_e2e_flow_test()
        },
        "execution_mode": "sequential",  # sequential | parallel
        "stop_on_failure": False,
        "mock_external": True,
        "timeout_per_test_ms": 5000,
        "status": "ready"
    }


def AI_make_l0_l1_flow_test() -> Dict[str, Any]:
    """
    Gantree: FlowSimulator → L0_L1_Flow_Test
    
    Purpose:
        L0(AIW) → L1(Telemetry) 데이터 플로우 테스트.
    
    Inputs:
        없음
    
    Outputs:
        - test: Dict - L0-L1 테스트 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "name": "L0_L1_Flow_Test",
        "description": "AIW Protocol → Telemetry Layer 데이터 플로우 검증",
        "test_cases": [
            {
                "id": "TC001",
                "name": "telemetry_ingest_basic",
                "input": {
                    "endpoint": "/telemetry/ingest",
                    "payload": {
                        "twin_id": "test_twin_1",
                        "asset_id": "test_asset_1",
                        "metrics": {"temp": 25.5, "pressure": 101.3}
                    }
                },
                "expected": {
                    "status": 200,
                    "event_published": True,
                    "event_type": "TelemetryAppended"
                }
            },
            {
                "id": "TC002",
                "name": "manifest_discovery",
                "input": {
                    "endpoint": "/.well-known/aiw-manifest.json",
                    "method": "GET"
                },
                "expected": {
                    "status": 200,
                    "contains_schemas": True,
                    "contains_endpoints": True
                }
            }
        ],
        "setup": ["mock_kafka", "mock_timescaledb"],
        "teardown": ["cleanup_test_data"]
    }


def AI_make_l1_l2_flow_test() -> Dict[str, Any]:
    """
    Gantree: FlowSimulator → L1_L2_Flow_Test
    
    Purpose:
        L1(Telemetry) → L2(Policy/Simulation) 데이터 플로우 테스트.
    
    Inputs:
        없음
    
    Outputs:
        - test: Dict - L1-L2 테스트 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "name": "L1_L2_Flow_Test",
        "description": "Telemetry → Policy/Simulation 데이터 플로우 검증",
        "test_cases": [
            {
                "id": "TC003",
                "name": "anomaly_triggers_policy",
                "input": {
                    "event_type": "AnomalyDetected",
                    "payload": {
                        "anomaly_id": "ano_test_1",
                        "twin_id": "test_twin_1",
                        "score": 0.92,
                        "kind": "drift"
                    }
                },
                "expected": {
                    "policy_evaluated": True,
                    "decision_type": "require_approval",  # 0.7 <= 0.92 < 0.9
                    "simulation_requested": True
                }
            },
            {
                "id": "TC004",
                "name": "simulation_result_updates_confidence",
                "input": {
                    "event_type": "SimulationCompleted",
                    "payload": {
                        "sim_id": "sim_test_1",
                        "kpi_distribution": {"yield": {"p50": 0.92}},
                        "uncertainty": {"yield_sigma": 0.01}
                    }
                },
                "expected": {
                    "confidence_updated": True,
                    "new_decision_evaluated": True
                }
            }
        ],
        "setup": ["inject_test_policy", "mock_simulation_engine"],
        "teardown": ["reset_policy_state"]
    }


def AI_make_e2e_flow_test() -> Dict[str, Any]:
    """
    Gantree: FlowSimulator → EndToEnd_Flow_Test
    
    Purpose:
        전체 E2E 플로우 테스트. Telemetry → Action 전체 경로.
    
    Inputs:
        없음
    
    Outputs:
        - test: Dict - E2E 테스트 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "name": "EndToEnd_Flow_Test",
        "description": "Telemetry → Anomaly → Policy → Simulation → Action 전체 검증",
        "test_cases": [
            {
                "id": "TC005",
                "name": "full_happy_path",
                "description": "정상 흐름: 이상 탐지 → 시뮬레이션 → 자동 실행",
                "steps": [
                    {"action": "inject_telemetry", "data": {"temp": 80.0}},
                    {"action": "wait_for_anomaly", "timeout_ms": 1000},
                    {"action": "verify_simulation_triggered"},
                    {"action": "mock_simulation_result", "confidence": 0.95},
                    {"action": "verify_auto_execute_decision"},
                    {"action": "verify_action_dispatched"},
                    {"action": "verify_audit_logged"}
                ],
                "expected": {
                    "all_steps_passed": True,
                    "action_status": "success",
                    "rollback_triggered": False
                }
            },
            {
                "id": "TC006",
                "name": "rollback_on_failure",
                "description": "실패 시 롤백 검증",
                "steps": [
                    {"action": "inject_telemetry", "data": {"temp": 85.0}},
                    {"action": "wait_for_anomaly", "timeout_ms": 1000},
                    {"action": "mock_simulation_result", "confidence": 0.95},
                    {"action": "mock_action_failure", "error": "connection_timeout"},
                    {"action": "verify_rollback_triggered"},
                    {"action": "verify_state_restored"}
                ],
                "expected": {
                    "rollback_triggered": True,
                    "state_restored": True,
                    "alert_sent": True
                }
            }
        ],
        "setup": ["full_mock_environment"],
        "teardown": ["full_cleanup"],
        "timeout_total_ms": 30000
    }


# =============================================================================
# ValidationReport 함수 (ValidationReportFunction)
# =============================================================================

def AI_make_validation_report() -> Dict[str, Any]:
    """
    Gantree: Phase0_5_DataFlow_Validation → ValidationReport
    
    Purpose:
        검증 리포트 생성기 초기화.
    
    Inputs:
        없음
    
    Outputs:
        - report_config: Dict - 검증 리포트 설정
    
    Dependencies:
        - AI_make_success_criteria()
        - AI_make_error_analysis()
        - AI_make_approval_gate()
    
    Status: Design
    """
    return {
        "success_criteria": AI_make_success_criteria(),
        "error_analysis": AI_make_error_analysis(),
        "approval_gate": AI_make_approval_gate(),
        "output_formats": ["json", "markdown", "html"],
        "include_details": True,
        "status": "ready"
    }


def AI_make_success_criteria() -> Dict[str, Any]:
    """
    Gantree: ValidationReport → SuccessCriteria
    
    Purpose:
        성공 기준 정의. Phase 0 완료 조건.
    
    Inputs:
        없음
    
    Outputs:
        - criteria: Dict - 성공 기준 목록
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "criteria": [
            {
                "id": "SC001",
                "name": "all_ppr_functions_defined",
                "description": "63개 PPR 함수 시그니처 정의 완료",
                "threshold": 63,
                "metric": "function_count",
                "required": True
            },
            {
                "id": "SC002",
                "name": "all_contracts_defined",
                "description": "4개 인터페이스 계약 명세 완료",
                "threshold": 4,
                "metric": "contract_count",
                "required": True
            },
            {
                "id": "SC003",
                "name": "l0_l1_tests_passed",
                "description": "L0-L1 플로우 테스트 통과",
                "threshold": 1.0,
                "metric": "test_pass_rate",
                "required": True
            },
            {
                "id": "SC004",
                "name": "l1_l2_tests_passed",
                "description": "L1-L2 플로우 테스트 통과",
                "threshold": 1.0,
                "metric": "test_pass_rate",
                "required": True
            },
            {
                "id": "SC005",
                "name": "e2e_tests_passed",
                "description": "E2E 플로우 테스트 통과",
                "threshold": 1.0,
                "metric": "test_pass_rate",
                "required": True
            },
            {
                "id": "SC006",
                "name": "no_critical_errors",
                "description": "Critical 에러 없음",
                "threshold": 0,
                "metric": "critical_error_count",
                "required": True
            }
        ],
        "overall_pass_condition": "all_required_met"
    }


def AI_make_error_analysis() -> Dict[str, Any]:
    """
    Gantree: ValidationReport → ErrorAnalysis
    
    Purpose:
        오류 분석 설정. 실패 원인 분류 및 권고.
    
    Inputs:
        없음
    
    Outputs:
        - analysis: Dict - 오류 분석 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "error_categories": [
            {
                "category": "schema_mismatch",
                "description": "스키마 불일치",
                "severity": "critical",
                "remediation": "스키마 버전 확인 및 동기화"
            },
            {
                "category": "contract_violation",
                "description": "계약 위반",
                "severity": "critical",
                "remediation": "인터페이스 계약 재검토"
            },
            {
                "category": "timeout",
                "description": "타임아웃",
                "severity": "high",
                "remediation": "타임아웃 임계값 조정 또는 성능 최적화"
            },
            {
                "category": "data_quality",
                "description": "데이터 품질 이슈",
                "severity": "medium",
                "remediation": "입력 데이터 검증 강화"
            },
            {
                "category": "mock_failure",
                "description": "Mock 설정 오류",
                "severity": "low",
                "remediation": "테스트 환경 설정 확인"
            }
        ],
        "root_cause_analysis": {
            "enabled": True,
            "depth": 3,  # 원인 분석 깊이
            "include_stack_trace": True
        }
    }


def AI_make_approval_gate() -> Dict[str, Any]:
    """
    Gantree: ValidationReport → ApprovalGate
    
    Purpose:
        승인 게이트. 구현 단계 진입 조건.
    
    Inputs:
        없음
    
    Outputs:
        - gate: Dict - 승인 게이트 설정
    
    Dependencies:
        없음
    
    Status: Design
    """
    return {
        "gate_conditions": [
            {
                "condition": "all_success_criteria_met",
                "action": "auto_approve",
                "next_phase": "Phase 1 MVP 구현"
            },
            {
                "condition": "critical_failures_exist",
                "action": "block",
                "next_phase": "None - 수정 필요"
            },
            {
                "condition": "warnings_only",
                "action": "require_manual_approval",
                "next_phase": "Phase 1 MVP 구현 (승인 후)"
            }
        ],
        "approvers": [
            {"role": "tech_lead", "required": True},
            {"role": "architect", "required": False}
        ],
        "approval_timeout_hours": 48,
        "auto_reject_on_timeout": False
    }
