# -*- coding: utf-8 -*-
"""
AIW SSE Publisher Module
========================

/subscribe 엔드포인트 SSE 이벤트 발행.
PPR 함수: AI_make_sse_publisher() 기반 구현.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional, Set


@dataclass
class SSEMessage:
    """SSE 메시지 데이터 클래스"""

    event: str
    data: Dict[str, Any]
    id: Optional[str] = None
    retry: Optional[int] = None

    def format(self) -> str:
        """SSE 형식으로 포맷"""
        lines = []
        if self.id:
            lines.append(f"id: {self.id}")
        if self.event:
            lines.append(f"event: {self.event}")
        if self.retry:
            lines.append(f"retry: {self.retry}")
        lines.append(f"data: {json.dumps(self.data)}")
        lines.append("")  # 빈 줄로 메시지 종료
        return "\n".join(lines) + "\n"


class SSEPublisher:
    """Server-Sent Events 발행자"""

    def __init__(self, max_connections: int = 1000):
        self.max_connections = max_connections
        self._subscribers: Set[asyncio.Queue] = set()
        self._event_buffer: List[SSEMessage] = []
        self._buffer_size = 100

    @property
    def subscriber_count(self) -> int:
        """현재 구독자 수"""
        return len(self._subscribers)

    async def subscribe(
        self,
        since_cursor: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """SSE 이벤트 스트림 구독"""
        if self.subscriber_count >= self.max_connections:
            yield SSEMessage(
                event="error",
                data={"message": "Max connections exceeded"},
            ).format()
            return

        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(queue)

        try:
            # 연결 확인 이벤트
            yield SSEMessage(
                event="connected",
                data={
                    "message": "Connected to OpsTwin SSE stream",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            ).format()

            # 이벤트 수신 루프
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield message.format()
                except asyncio.TimeoutError:
                    # 30초마다 heartbeat
                    yield SSEMessage(
                        event="heartbeat",
                        data={"timestamp": datetime.utcnow().isoformat() + "Z"},
                    ).format()
        finally:
            self._subscribers.discard(queue)

    async def publish(
        self,
        event_type: str,
        twin_id: str,
        event_id: str,
        data: Dict[str, Any],
    ) -> None:
        """이벤트 발행 (모든 구독자에게)"""
        message = SSEMessage(
            event=event_type,
            data={
                "type": event_type,
                "ts": datetime.utcnow().isoformat() + "Z",
                "twin_id": twin_id,
                "id": event_id,
                "data": data,
            },
            id=event_id,
        )

        # 버퍼에 저장
        self._event_buffer.append(message)
        if len(self._event_buffer) > self._buffer_size:
            self._event_buffer.pop(0)

        # 모든 구독자에게 전달
        for queue in self._subscribers:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass  # 큐가 가득 차면 드롭

    async def publish_telemetry_appended(
        self,
        twin_id: str,
        telemetry_id: str,
        asset_id: str,
    ) -> None:
        """TelemetryAppended 이벤트 발행"""
        await self.publish(
            event_type="TelemetryAppended",
            twin_id=twin_id,
            event_id=telemetry_id,
            data={
                "data_ref": {"type": "telemetry", "id": telemetry_id},
                "asset_id": asset_id,
            },
        )

    async def publish_anomaly_detected(
        self,
        twin_id: str,
        anomaly_id: str,
        score: float,
        kind: str,
    ) -> None:
        """AnomalyDetected 이벤트 발행"""
        await self.publish(
            event_type="AnomalyDetected",
            twin_id=twin_id,
            event_id=anomaly_id,
            data={
                "data_ref": {"type": "anomaly", "id": anomaly_id},
                "score": score,
                "kind": kind,
            },
        )


# 싱글톤 인스턴스
sse_publisher = SSEPublisher()
