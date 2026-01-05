# -*- coding: utf-8 -*-
"""
Sensor Adapter Module
=====================

센서 데이터 수집 어댑터.
PPR 함수: AI_make_sensor_adapter() 기반 구현.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SensorConfig:
    """센서 설정"""

    sensor_id: str
    sensor_type: str  # mqtt, opc-ua, modbus, plc
    endpoint: str
    polling_interval_ms: int = 1000
    timeout_ms: int = 5000
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SensorReading:
    """센서 읽기 데이터"""

    sensor_id: str
    timestamp: str
    metrics: Dict[str, float]
    quality: float = 1.0  # 0.0 ~ 1.0


class SensorAdapter(ABC):
    """센서 어댑터 추상 클래스"""

    def __init__(self, config: SensorConfig):
        self.config = config
        self._connected = False
        self._callbacks: List[Callable[[SensorReading], None]] = []

    @property
    def is_connected(self) -> bool:
        return self._connected

    @abstractmethod
    async def connect(self) -> bool:
        """센서 연결"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """센서 연결 해제"""
        pass

    @abstractmethod
    async def read(self) -> Optional[SensorReading]:
        """센서 데이터 읽기"""
        pass

    def on_reading(self, callback: Callable[[SensorReading], None]) -> None:
        """읽기 콜백 등록"""
        self._callbacks.append(callback)

    async def _notify_callbacks(self, reading: SensorReading) -> None:
        """콜백 호출"""
        for callback in self._callbacks:
            try:
                callback(reading)
            except Exception:
                pass  # 콜백 에러는 무시


class MQTTSensorAdapter(SensorAdapter):
    """MQTT 센서 어댑터 (MVP 구현)"""

    def __init__(self, config: SensorConfig):
        super().__init__(config)
        self._client = None
        self._topic = config.metadata.get("topic", f"sensors/{config.sensor_id}")

    async def connect(self) -> bool:
        """MQTT 브로커 연결"""
        # MVP: 실제 MQTT 연결 대신 시뮬레이션
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """MQTT 연결 해제"""
        self._connected = False

    async def read(self) -> Optional[SensorReading]:
        """MQTT 메시지 읽기 (시뮬레이션)"""
        if not self._connected:
            return None

        # MVP: 시뮬레이션 데이터
        import random

        reading = SensorReading(
            sensor_id=self.config.sensor_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            metrics={
                "temperature": round(20 + random.gauss(0, 2), 2),
                "humidity": round(50 + random.gauss(0, 5), 2),
                "pressure": round(1013 + random.gauss(0, 10), 2),
            },
            quality=1.0,
        )

        await self._notify_callbacks(reading)
        return reading

    async def start_polling(self) -> None:
        """주기적 폴링 시작"""
        while self._connected:
            await self.read()
            await asyncio.sleep(self.config.polling_interval_ms / 1000)


class OPCUASensorAdapter(SensorAdapter):
    """OPC-UA 센서 어댑터 (Phase 1.2+ 구현 예정)"""

    async def connect(self) -> bool:
        raise NotImplementedError("OPC-UA adapter not yet implemented")

    async def disconnect(self) -> None:
        pass

    async def read(self) -> Optional[SensorReading]:
        return None


def create_sensor_adapter(config: SensorConfig) -> SensorAdapter:
    """센서 타입에 따른 어댑터 팩토리"""
    adapters = {
        "mqtt": MQTTSensorAdapter,
        "opc-ua": OPCUASensorAdapter,
    }
    adapter_class = adapters.get(config.sensor_type, MQTTSensorAdapter)
    return adapter_class(config)
