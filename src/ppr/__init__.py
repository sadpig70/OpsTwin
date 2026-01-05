# -*- coding: utf-8 -*-
"""
OpsTwin PPR 함수 패키지
======================

PPR (Purposeful-Programming Revolution) 함수 정의 모음.
각 Phase별로 분리된 모듈에서 함수를 re-export.

Modules:
    - aiw_protocol: AIW 프로토콜 관련 함수 (Phase 0.1)
    - telemetry_layer: 텔레메트리 레이어 함수 (Phase 0.2)
    - policy_engine: 정책 엔진 함수 (Phase 0.3)
    - simulation_engine: 시뮬레이션 엔진 함수 (Phase 0.4)
    - data_flow_validator: 데이터 플로우 검증 함수 (Phase 0.5)
"""

from .aiw_protocol import *
from .data_flow_validator import *
from .policy_engine import *
from .simulation_engine import *
from .telemetry_layer import *

__version__ = "0.1.0"
__all__ = [
    # Phase 0.1: AIW Protocol
    'AI_make_manifest',
    'AI_make_manifest_schema',
    'AI_make_endpoint_registry',
    'AI_make_capability_declaration',
    'AI_make_diff_stream',
    'AI_make_diff_engine',
    'AI_make_sse_publisher',
    'AI_make_cursor_manager',
    'AI_make_schema_registry',
    'AI_make_telemetry_schema',
    'AI_make_action_schema',
    'AI_make_policy_schema',
    # Phase 0.2: Telemetry Layer
    'AI_make_data_collector',
    'AI_make_sensor_adapter',
    'AI_make_log_ingester',
    'AI_make_metric_aggregator',
    'AI_make_stream_processor',
    'AI_make_kafka_connector',
    'AI_make_event_normalizer',
    'AI_make_anomaly_detector',
    'AI_make_timeseries_db',
    'AI_make_timescale_adapter',
    'AI_make_retention_manager',
    # Phase 0.3: Policy Engine
    'AI_make_permission_model',
    'AI_make_role_manager',
    'AI_make_permission_checker',
    'AI_make_audit_logger',
    'AI_make_policy_evaluator',
    'AI_make_condition_parser',
    'AI_make_confidence_scorer',
    'AI_make_decision_maker',
    'AI_make_approval_workflow',
    'AI_make_proposal_generator',
    'AI_make_human_interface',
    'AI_make_feedback_processor',
    'AI_make_rollback_manager',
    'AI_make_state_snapshot',
    'AI_make_rollback_executor',
    'AI_make_merkle_audit_log',
    # Phase 0.4: Simulation Engine
    'AI_make_classical_simulator',
    'AI_make_monte_carlo_engine',
    'AI_make_physics_engine',
    'AI_make_optimization_solver',
    'AI_make_quantum_simulator',
    'AI_make_qiskit_bridge',
    'AI_make_qaoa_optimizer',
    'AI_make_vqe_solver',
    'AI_make_hybrid_coupler',
    'AI_make_task_classifier',
    'AI_make_result_fusion',
    # Phase 0.5: Data Flow Validator
    'AI_make_interface_contract',
    'AI_make_aiw_telemetry_contract',
    'AI_make_telemetry_policy_contract',
    'AI_make_policy_simulation_contract',
    'AI_make_simulation_action_contract',
    'AI_make_flow_simulator',
    'AI_make_l0_l1_flow_test',
    'AI_make_l1_l2_flow_test',
    'AI_make_e2e_flow_test',
    'AI_make_validation_report',
    'AI_make_success_criteria',
    'AI_make_error_analysis',
    'AI_make_approval_gate',
]
