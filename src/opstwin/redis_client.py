# -*- coding: utf-8 -*-
"""
Redis Client Module
===================

Redis 연결 관리.
커서 관리, 캐싱, 세션 등에 사용.
"""

import json
from typing import Any, Optional

import redis.asyncio as redis

from src.opstwin.config import settings


class RedisClient:
    """Redis 비동기 클라이언트"""

    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.redis_url
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Redis 연결"""
        self._pool = redis.ConnectionPool.from_url(
            self.url,
            max_connections=20,
            decode_responses=True,
        )
        self._client = redis.Redis(connection_pool=self._pool)
        # 연결 테스트
        await self._client.ping()

    async def disconnect(self) -> None:
        """연결 해제"""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()

    @property
    def client(self) -> redis.Redis:
        """Redis 클라이언트 반환"""
        if self._client is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client

    # === 커서 관리 ===

    async def get_cursor(self, subscriber_id: str) -> str:
        """구독자의 현재 커서 조회"""
        key = f"cursor:{subscriber_id}"
        cursor = await self.client.get(key)
        return cursor or "cursor_000000"

    async def set_cursor(self, subscriber_id: str, cursor: str, ttl_seconds: int = 86400) -> None:
        """구독자의 커서 업데이트"""
        key = f"cursor:{subscriber_id}"
        await self.client.set(key, cursor, ex=ttl_seconds)

    async def get_global_cursor(self) -> int:
        """전역 커서 오프셋 조회"""
        offset = await self.client.get("cursor:global")
        return int(offset) if offset else 0

    async def increment_global_cursor(self) -> int:
        """전역 커서 증가"""
        return await self.client.incr("cursor:global")

    # === 이벤트 버퍼 ===

    async def push_event(self, event: dict, max_buffer_size: int = 10000) -> None:
        """이벤트 버퍼에 추가"""
        event_json = json.dumps(event)
        await self.client.lpush("events:buffer", event_json)
        await self.client.ltrim("events:buffer", 0, max_buffer_size - 1)

    async def get_events_since(self, offset: int, limit: int = 100) -> list:
        """오프셋 이후의 이벤트 조회"""
        end = offset + limit - 1
        events_json = await self.client.lrange("events:buffer", offset, end)
        return [json.loads(e) for e in events_json]

    # === 캐싱 ===

    async def cache_get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        data = await self.client.get(f"cache:{key}")
        if data:
            return json.loads(data)
        return None

    async def cache_set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """캐시 저장"""
        await self.client.set(f"cache:{key}", json.dumps(value), ex=ttl_seconds)

    async def cache_delete(self, key: str) -> None:
        """캐시 삭제"""
        await self.client.delete(f"cache:{key}")

    # === Pub/Sub ===

    async def publish(self, channel: str, message: dict) -> int:
        """메시지 발행"""
        return await self.client.publish(channel, json.dumps(message))

    def subscribe(self, *channels: str):
        """채널 구독 (Pub/Sub)"""
        pubsub = self.client.pubsub()
        return pubsub.subscribe(*channels)


# 싱글톤 인스턴스
redis_client = RedisClient()
