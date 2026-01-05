# -*- coding: utf-8 -*-
"""
Database Module
===============

TimescaleDB 鍮꾨룞湲??곌껐 愿由?
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

import asyncpg

from src.opstwin.config import settings


class Database:
    """TimescaleDB 鍮꾨룞湲??곗씠?곕쿋?댁뒪"""

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or settings.database_url
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """?곗씠?곕쿋?댁뒪 ?곌껐 ? ?앹꽦"""
        self._pool = await asyncpg.create_pool(
            self.dsn,
            min_size=5,
            max_size=settings.database_pool_size,
            command_timeout=60,
        )

    async def disconnect(self) -> None:
        """?곌껐 ? 醫낅즺"""
        if self._pool:
            await self._pool.close()

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """?곌껐 ?띾뱷"""
        if self._pool is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        async with self._pool.acquire() as conn:
            yield conn

    async def execute(self, query: str, *args) -> str:
        """荑쇰━ ?ㅽ뻾"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """?ㅼ쨷 ??議고쉶"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """?⑥씪 ??議고쉶"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """?⑥씪 媛?議고쉶"""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)


class TelemetryRepository:
    """?붾젅硫뷀듃由??덊룷吏?좊━"""

    TABLE_NAME = "telemetry_events"

    def __init__(self, db: Database):
        self.db = db

    async def create_table(self) -> None:
        """?뚯씠釉??앹꽦 (Hypertable)"""
        await self.db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                ts TIMESTAMPTZ NOT NULL,
                event_id TEXT NOT NULL,
                twin_id TEXT NOT NULL,
                asset_id TEXT NOT NULL,
                metrics JSONB NOT NULL,
                tags JSONB,
                quality JSONB,
                PRIMARY KEY (ts, event_id)
            );
        """)

        # Hypertable 蹂??(TimescaleDB)
        try:
            await self.db.execute(f"""
                SELECT create_hypertable('{self.TABLE_NAME}', 'ts',
                    if_not_exists => TRUE);
            """)
        except Exception:
            pass  # ?대? hypertable??寃쎌슦

    async def insert(self, data: Dict[str, Any]) -> str:
        """?붾젅硫뷀듃由??쎌엯"""
        import json

        await self.db.execute(
            f"""
            INSERT INTO {self.TABLE_NAME}
            (ts, event_id, twin_id, asset_id, metrics, tags, quality)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
            datetime.fromisoformat(data["ts"].replace("Z", "+00:00")),
            data["event_id"],
            data["twin_id"],
            data["asset_id"],
            json.dumps(data["metrics"]),
            json.dumps(data.get("tags", {})),
            json.dumps(data.get("quality", {})),
        )
        return data["event_id"]

    async def insert_batch(self, records: List[Dict[str, Any]]) -> int:
        """諛곗튂 ?쎌엯"""
        for record in records:
            await self.insert(record)
        return len(records)

    async def query(
        self,
        twin_id: str,
        asset_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """?붾젅硫뷀듃由?議고쉶"""
        conditions = ["twin_id = $1"]
        params = [twin_id]
        param_idx = 2

        if asset_id:
            conditions.append(f"asset_id = ${param_idx}")
            params.append(asset_id)
            param_idx += 1

        if start_time:
            conditions.append(f"ts >= ${param_idx}")
            params.append(datetime.fromisoformat(start_time.replace("Z", "+00:00")))
            param_idx += 1

        if end_time:
            conditions.append(f"ts <= ${param_idx}")
            params.append(datetime.fromisoformat(end_time.replace("Z", "+00:00")))
            param_idx += 1

        where = " AND ".join(conditions)

        rows = await self.db.fetch(
            f"""
            SELECT ts, event_id, twin_id, asset_id, metrics, tags, quality
            FROM {self.TABLE_NAME}
            WHERE {where}
            ORDER BY ts DESC
            LIMIT {limit}
        """,
            *params,
        )

        return [
            {
                "ts": row["ts"].isoformat(),
                "event_id": row["event_id"],
                "twin_id": row["twin_id"],
                "asset_id": row["asset_id"],
                "metrics": row["metrics"],
                "tags": row["tags"],
                "quality": row["quality"],
            }
            for row in rows
        ]

    async def aggregate(
        self,
        twin_id: str,
        metric_name: str,
        window: str = "1 minute",
        function: str = "avg",
    ) -> List[Dict[str, Any]]:
        """?쒓퀎??吏묎퀎 (TimescaleDB time_bucket)"""
        rows = await self.db.fetch(
            f"""
            SELECT
                time_bucket('{window}', ts) AS bucket,
                {function}((metrics->>$2)::float) AS value,
                COUNT(*) AS count
            FROM {self.TABLE_NAME}
            WHERE twin_id = $1 AND metrics ? $2
            GROUP BY bucket
            ORDER BY bucket DESC
            LIMIT 100
        """,
            twin_id,
            metric_name,
        )

        return [
            {
                "bucket": row["bucket"].isoformat(),
                "value": float(row["value"]) if row["value"] else None,
                "count": row["count"],
            }
            for row in rows
        ]


# ?깃????몄뒪?댁뒪
database = Database()
telemetry_repo = TelemetryRepository(database)
