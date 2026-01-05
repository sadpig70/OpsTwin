# -*- coding: utf-8 -*-
"""
Permission Model Module
=======================

RBAC 기반 권한 관리.
PPR 함수: AI_make_permission_model() 기반 구현.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class Permission(str, Enum):
    """권한 열거형"""

    READ = "read"
    PROPOSE = "propose"
    APPROVE = "approve"
    EXECUTE = "execute"


@dataclass
class Role:
    """역할 정의"""

    name: str
    permissions: Set[Permission]
    scope: Optional[str] = None  # twin_id 또는 asset_id 패턴

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions


@dataclass
class User:
    """사용자"""

    user_id: str
    roles: List[str]
    attributes: Dict[str, Any] = field(default_factory=dict)


class PermissionChecker:
    """권한 검사기"""

    # 기본 역할 정의
    DEFAULT_ROLES = {
        "viewer": Role("viewer", {Permission.READ}),
        "agent": Role("agent", {Permission.READ, Permission.PROPOSE}),
        "supervisor": Role("supervisor", {Permission.READ, Permission.PROPOSE, Permission.APPROVE}),
        "executor": Role("executor", {Permission.READ, Permission.EXECUTE}),
        "admin": Role(
            "admin", {Permission.READ, Permission.PROPOSE, Permission.APPROVE, Permission.EXECUTE}
        ),
    }

    # 역할 계층
    ROLE_HIERARCHY = {
        "admin": ["supervisor", "executor"],
        "supervisor": ["agent", "viewer"],
        "executor": ["viewer"],
        "agent": ["viewer"],
    }

    def __init__(self):
        self._roles: Dict[str, Role] = dict(self.DEFAULT_ROLES)
        self._user_roles: Dict[str, Set[str]] = {}
        self._audit_log: List[Dict[str, Any]] = []

    def register_role(self, role: Role) -> None:
        """커스텀 역할 등록"""
        self._roles[role.name] = role

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """사용자에게 역할 할당"""
        if role_name not in self._roles:
            return False

        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()

        self._user_roles[user_id].add(role_name)
        return True

    def check_permission(
        self,
        user_id: str,
        permission: Permission,
        resource_id: Optional[str] = None,
    ) -> bool:
        """권한 검사"""
        user_roles = self._get_effective_roles(user_id)

        for role_name in user_roles:
            role = self._roles.get(role_name)
            if role and role.has_permission(permission):
                # 범위 검사
                if role.scope and resource_id:
                    if not self._match_scope(role.scope, resource_id):
                        continue

                self._log_access(user_id, permission, resource_id, True)
                return True

        self._log_access(user_id, permission, resource_id, False)
        return False

    def require_permission(
        self,
        user_id: str,
        permission: Permission,
        resource_id: Optional[str] = None,
    ) -> None:
        """권한 검사 (실패 시 예외)"""
        if not self.check_permission(user_id, permission, resource_id):
            raise PermissionError(
                f"User {user_id} lacks {permission.value} permission"
                + (f" for {resource_id}" if resource_id else "")
            )

    def _get_effective_roles(self, user_id: str) -> Set[str]:
        """유효 역할 조회 (계층 포함)"""
        direct_roles = self._user_roles.get(user_id, set())
        effective = set(direct_roles)

        for role_name in list(effective):
            inherited = self.ROLE_HIERARCHY.get(role_name, [])
            effective.update(inherited)

        return effective

    def _match_scope(self, scope_pattern: str, resource_id: str) -> bool:
        """범위 패턴 매칭"""
        import fnmatch

        return fnmatch.fnmatch(resource_id, scope_pattern)

    def _log_access(
        self,
        user_id: str,
        permission: Permission,
        resource_id: Optional[str],
        result: bool,
    ) -> None:
        """접근 로그 기록"""
        from datetime import datetime

        self._audit_log.append(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_id": user_id,
                "permission": permission.value,
                "resource_id": resource_id,
                "result": "granted" if result else "denied",
            }
        )

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """감사 로그 조회"""
        return self._audit_log[-limit:]


# 싱글톤 인스턴스
permission_checker = PermissionChecker()
