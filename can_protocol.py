"""CAN message definitions for the virtual cockpit controller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CANMessage:
    """Simple CAN frame representation."""

    arbitration_id: int
    data: List[int]
    dlc: int

    @classmethod
    def from_bytes(cls, arbitration_id: int, payload: bytes) -> "CANMessage":
        data = list(payload)
        return cls(arbitration_id=arbitration_id, data=data, dlc=len(data))

    def to_bytes(self) -> bytes:
        return bytes(self.data)


class CANProtocol:
    """Defines message IDs and payload rules for vehicle dashboard signals."""

    RPM_ID = 0x101
    SPEED_ID = 0x102
    FUEL_ID = 0x103
    LIGHTS_ID = 0x104
    WIPER_ID = 0x105

    @staticmethod
    def encode_rpm(value: int) -> CANMessage:
        return CANMessage.from_bytes(CANProtocol.RPM_ID, bytes([value & 0xFF, (value >> 8) & 0xFF]))

    @staticmethod
    def decode_rpm(frame: CANMessage) -> int:
        return frame.data[0] | (frame.data[1] << 8)

    @staticmethod
    def encode_speed(value: int) -> CANMessage:
        return CANMessage.from_bytes(CANProtocol.SPEED_ID, bytes([value & 0xFF]))

    @staticmethod
    def decode_speed(frame: CANMessage) -> int:
        return frame.data[0]

    @staticmethod
    def encode_fuel(value: int) -> CANMessage:
        return CANMessage.from_bytes(CANProtocol.FUEL_ID, bytes([value & 0xFF]))

    @staticmethod
    def decode_fuel(frame: CANMessage) -> int:
        return frame.data[0]

    @staticmethod
    def encode_lights(left: bool, right: bool, brake: bool, hazard: bool) -> CANMessage:
        mask = 0
        if left:
            mask |= 0b0001
        if right:
            mask |= 0b0010
        if brake:
            mask |= 0b0100
        if hazard:
            mask |= 0b1000
        return CANMessage.from_bytes(CANProtocol.LIGHTS_ID, bytes([mask]))

    @staticmethod
    def decode_lights(frame: CANMessage) -> Dict[str, bool]:
        mask = frame.data[0] if frame.data else 0
        return {
            "left": bool(mask & 0b0001),
            "right": bool(mask & 0b0010),
            "brake": bool(mask & 0b0100),
            "hazard": bool(mask & 0b1000),
        }

    @staticmethod
    def encode_wiper(mode: str) -> CANMessage:
        mapping = {"off": 0, "low": 1, "high": 2, "auto": 3}
        mode_value = mapping.get(mode.lower(), 0)
        return CANMessage.from_bytes(CANProtocol.WIPER_ID, bytes([mode_value]))

    @staticmethod
    def decode_wiper(frame: CANMessage) -> str:
        mode_map = {0: "off", 1: "low", 2: "high", 3: "auto"}
        raw = frame.data[0] if frame.data else 0
        return mode_map.get(raw, "off")
