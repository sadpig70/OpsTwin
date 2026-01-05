# -*- coding: utf-8 -*-
"""
Diff Route
==========

/diff, /subscribe 엔드포인트.
"""

from typing import Optional

from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse

from src.opstwin.aiw.diff_stream import DiffEngine
from src.opstwin.aiw.sse_publisher import sse_publisher

router = APIRouter(tags=["AIW Protocol"])

# 전역 DiffEngine 인스턴스
diff_engine = DiffEngine()


@router.get("/diff")
async def get_diff(
    since: Optional[str] = Query(None, description="시작 커서"),
    limit: int = Query(100, ge=1, le=5000, description="최대 이벤트 수"),
):
    """Delta Sync - 커서 이후의 변경분 조회"""
    result = diff_engine.get_events(since_cursor=since, limit=limit)
    return result


@router.get("/subscribe")
async def subscribe(
    since: Optional[str] = Query(None, description="시작 커서"),
):
    """SSE 이벤트 스트림 구독"""
    return EventSourceResponse(
        sse_publisher.subscribe(since_cursor=since),
        media_type="text/event-stream",
    )
