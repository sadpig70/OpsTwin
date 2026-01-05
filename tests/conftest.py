# -*- coding: utf-8 -*-
"""
Pytest Configuration
====================

공통 fixtures 및 설정.
"""

import sys
from pathlib import Path

import pytest

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_telemetry():
    """샘플 텔레메트리 데이터"""
    return {
        "twin_id": "twin_test_001",
        "asset_id": "asset_test_001",
        "metrics": {
            "temperature": 25.5,
            "humidity": 60.2,
            "pressure": 1013.25,
        },
        "tags": {"location": "factory_a"},
    }


@pytest.fixture
def sample_anomaly():
    """샘플 이상 데이터"""
    return {
        "anomaly_id": "ano_test_001",
        "twin_id": "twin_test_001",
        "asset_id": "asset_test_001",
        "score": 0.85,
        "kind": "spike",
    }


@pytest.fixture
def sample_user():
    """샘플 사용자"""
    return {
        "user_id": "user_test_001",
        "roles": ["agent"],
    }


@pytest.fixture
def admin_user():
    """관리자 사용자"""
    return {
        "user_id": "admin_test_001",
        "roles": ["admin"],
    }
