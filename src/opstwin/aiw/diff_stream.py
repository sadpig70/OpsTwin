# -*- coding: utf-8 -*-
"""
AIW Diff Stream Module
======================

/diff 엔드포인트 및 커서 관리.
PPR 함수: AI_make_diff_engine(), AI_make_cursor_manager() 기반 구현.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DiffEvent:
    """Diff 이벤트 데이터 클래스"""

    event_type: str
    timestamp: str
    twin_id: str
    event_id: str
    data_ref: Dict[str, str]
    data: Optional[Dict[str, Any]] = None


class CursorManager:
    """구독자별 커서 관리"""

    INITIAL_CURSOR = "cursor_000000"

    def __init__(self):
        # 실제 구현에서는 Redis 사용
        self._cursors: Dict[str, str] = {}
        self._event_log: List[DiffEvent] = []
        self._current_offset: int = 0

    def get_cursor(self, subscriber_id: str) -> str:
        """구독자의 현재 커서 조회"""
        return self._cursors.get(subscriber_id, self.INITIAL_CURSOR)

    def set_cursor(self, subscriber_id: str, cursor: str) -> None:
        """구독자의 커서 업데이트"""
        self._cursors[subscriber_id] = cursor

    def parse_cursor(self, cursor: str) -> int:
        """커서 문자열을 오프셋으로 변환"""
        try:
            return int(cursor.split("_")[1])
        except (IndexError, ValueError):
            return 0

    def format_cursor(self, offset: int) -> str:
        """오프셋을 커서 문자열로 변환"""
        return f"cursor_{offset:06d}"

    def append_event(self, event: DiffEvent) -> str:
        """이벤트 로그에 추가하고 커서 반환"""
        self._current_offset += 1
        self._event_log.append(event)
        return self.format_cursor(self._current_offset)


class DiffEngine:
    """Diff 엔진 - 변경분 조회"""

    def __init__(self, cursor_manager: Optional[CursorManager] = None):
        self.cursor_manager = cursor_manager or CursorManager()

    def get_events(
        self,
        since_cursor: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """커서 이후의 이벤트 조회"""
        cursor = since_cursor or CursorManager.INITIAL_CURSOR
        offset = self.cursor_manager.parse_cursor(cursor)

        # 이벤트 로그에서 조회
        events = self.cursor_manager._event_log[offset : offset + limit]

        # 다음 커서 계산
        next_offset = offset + len(events)
        next_cursor = self.cursor_manager.format_cursor(next_offset)

        return {
            "since": cursor,
            "next_cursor": next_cursor,
            "events": [self._serialize_event(e) for e in events],
        }

    def append_event(
        self,
        event_type: str,
        twin_id: str,
        data_ref: Dict[str, str],
        data: Optional[Dict[str, Any]] = None,
    ) -> DiffEvent:
        """새 이벤트 추가"""
        event = DiffEvent(
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            twin_id=twin_id,
            event_id=f"evt_{self.cursor_manager._current_offset + 1:08d}",
            data_ref=data_ref,
            data=data,
        )
        self.cursor_manager.append_event(event)
        return event

    def _serialize_event(self, event: DiffEvent) -> Dict[str, Any]:
        """이벤트를 딕셔너리로 변환"""
        result = {
            "type": event.event_type,
            "ts": event.timestamp,
            "twin_id": event.twin_id,
            "id": event.event_id,
            "data_ref": event.data_ref,
        }
        if event.data:
            result["data"] = event.data
        return result
