# -*- coding: utf-8 -*-
"""
Telemetry Route
===============

/telemetry/ingest 엔드포인트.
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.opstwin.aiw.diff_stream import DiffEngine
from src.opstwin.aiw.schema_registry import schema_registry
from src.opstwin.aiw.sse_publisher import sse_publisher

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

# 전역 인스턴스
diff_engine = DiffEngine()


class TelemetryIngestRequest(BaseModel):
    """텔레메트리 수집 요청"""

    twin_id: str = Field(..., description="트윈 식별자")
    asset_id: str = Field(..., description="자산 식별자")
    metrics: Dict[str, float] = Field(..., description="메트릭 키-값")
    tags: Optional[Dict[str, str]] = Field(default=None, description="태그")
    ts: Optional[str] = Field(default=None, description="타임스탬프 (RFC3339)")


class TelemetryIngestResponse(BaseModel):
    """텔레메트리 수집 응답"""

    event_id: str
    status: str
    message: str


@router.post("/ingest", response_model=TelemetryIngestResponse)
async def ingest_telemetry(request: TelemetryIngestRequest):
    """텔레메트리 데이터 수집"""
    # 이벤트 ID 생성
    event_id = f"tel_{uuid4().hex[:12]}"

    # 타임스탬프 설정
    ts = request.ts or (datetime.utcnow().isoformat() + "Z")

    # 전체 텔레메트리 데이터
    telemetry_data = {
        "event_id": event_id,
        "twin_id": request.twin_id,
        "asset_id": request.asset_id,
        "ts": ts,
        "metrics": request.metrics,
        "tags": request.tags or {},
    }

    # 스키마 검증
    errors = schema_registry.validate("telemetry.v1", telemetry_data)
    if errors:
        raise HTTPException(status_code=400, detail={"validation_errors": errors})

    # TimescaleDB 저장 (선택적)
    try:
        from src.opstwin.database import telemetry_repo

        await telemetry_repo.insert(telemetry_data)
    except Exception:
        pass  # MVP 모드: DB 없이도 동작

    # Redis 이벤트 버퍼에 추가 (선택적)
    try:
        from src.opstwin.redis_client import redis_client

        await redis_client.push_event(
            {
                "type": "TelemetryAppended",
                "twin_id": request.twin_id,
                "event_id": event_id,
                "ts": ts,
            }
        )
    except Exception:
        pass  # MVP 모드

    # Diff 이벤트 추가 (인메모리)
    diff_engine.append_event(
        event_type="TelemetryAppended",
        twin_id=request.twin_id,
        data_ref={"type": "telemetry", "id": event_id},
        data=telemetry_data,
    )

    # SSE 이벤트 발행
    await sse_publisher.publish_telemetry_appended(
        twin_id=request.twin_id,
        telemetry_id=event_id,
        asset_id=request.asset_id,
    )

    return TelemetryIngestResponse(
        event_id=event_id,
        status="accepted",
        message="Telemetry data ingested successfully",
    )


@router.get("/query")
async def query_telemetry(
    twin_id: str,
    asset_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
):
    """텔레메트리 데이터 조회"""
    try:
        from src.opstwin.database import telemetry_repo

        rows = await telemetry_repo.query(
            twin_id=twin_id,
            asset_id=asset_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        return {"rows": rows, "count": len(rows)}
    except Exception as e:
        return {"rows": [], "count": 0, "error": str(e)}


@router.get("/aggregate")
async def aggregate_telemetry(
    twin_id: str,
    metric_name: str,
    window: str = "1 minute",
    function: str = "avg",
):
    """텔레메트리 시계열 집계"""
    try:
        from src.opstwin.database import telemetry_repo

        result = await telemetry_repo.aggregate(
            twin_id=twin_id,
            metric_name=metric_name,
            window=window,
            function=function,
        )
        return {"buckets": result}
    except Exception as e:
        return {"buckets": [], "error": str(e)}
