# -*- coding: utf-8 -*-
"""
Time Series DB Module
=====================

TimescaleDB 어댑터.
PPR 함수: AI_make_timescale_adapter() 기반 구현.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from src.opstwin.config import settings


@dataclass
class QueryResult:
    """쿼리 결과"""

    rows: List[Dict[str, Any]]
    count: int
    execution_time_ms: float


class TimeSeriesDB:
    """TimescaleDB 어댑터"""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or settings.database_url
        self._pool = None
        self._connected = False

        # 인메모리 저장소 (MVP)
        self._data: List[Dict[str, Any]] = []

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        """데이터베이스 연결"""
        # MVP: 인메모리 모드
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """연결 해제"""
        self._connected = False
        self._pool = None

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator:
        """연결 컨텍스트 매니저"""
        if not self._connected:
            await self.connect()
        try:
            yield self
        finally:
            pass  # 풀 사용 시 여기서 반환

    async def insert_telemetry(self, data: Dict[str, Any]) -> str:
        """텔레메트리 데이터 삽입"""
        if not self._connected:
            await self.connect()

        # MVP: 인메모리 저장
        self._data.append(
            {
                **data,
                "_inserted_at": datetime.utcnow().isoformat() + "Z",
            }
        )

        return data.get("event_id", "unknown")

    async def insert_batch(self, records: List[Dict[str, Any]]) -> int:
        """배치 삽입"""
        for record in records:
            await self.insert_telemetry(record)
        return len(records)

    async def query_telemetry(
        self,
        twin_id: str,
        asset_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
    ) -> QueryResult:
        """텔레메트리 데이터 조회"""
        import time

        start = time.time()

        results = []
        for record in self._data:
            if record.get("twin_id") != twin_id:
                continue
            if asset_id and record.get("asset_id") != asset_id:
                continue
            if start_time and record.get("ts", "") < start_time:
                continue
            if end_time and record.get("ts", "") > end_time:
                continue
            results.append(record)
            if len(results) >= limit:
                break

        execution_time = (time.time() - start) * 1000

        return QueryResult(
            rows=results,
            count=len(results),
            execution_time_ms=round(execution_time, 2),
        )

    async def aggregate(
        self,
        twin_id: str,
        metric_name: str,
        window_seconds: int = 60,
        function: str = "mean",
    ) -> List[Dict[str, Any]]:
        """집계 쿼리"""
        # MVP: 간단한 집계
        values = []
        for record in self._data:
            if record.get("twin_id") != twin_id:
                continue
            metrics = record.get("metrics", {})
            if metric_name in metrics:
                values.append(metrics[metric_name])

        if not values:
            return []

        import numpy as np

        agg_funcs = {
            "mean": np.mean,
            "sum": np.sum,
            "min": np.min,
            "max": np.max,
            "std": np.std,
            "count": len,
        }

        func = agg_funcs.get(function, np.mean)
        result = func(values)

        return [
            {
                "twin_id": twin_id,
                "metric": metric_name,
                "window_seconds": window_seconds,
                "function": function,
                "value": float(result),
                "sample_count": len(values),
            }
        ]

    async def get_latest(
        self,
        twin_id: str,
        asset_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """최신 데이터 조회"""
        for record in reversed(self._data):
            if record.get("twin_id") != twin_id:
                continue
            if asset_id and record.get("asset_id") != asset_id:
                continue
            return record
        return None

    def clear(self) -> None:
        """인메모리 데이터 초기화 (테스트용)"""
        self._data.clear()


# 싱글톤 인스턴스
timeseries_db = TimeSeriesDB()
