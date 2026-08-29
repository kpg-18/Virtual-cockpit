"""Stateful virtual cockpit controller."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from can_protocol import CANMessage, CANProtocol


@dataclass
class DashboardState:
    rpm: int = 0
    speed: int = 0
    fuel: int = 100
    left_indicator: bool = False
    right_indicator: bool = False
    brake_light: bool = False
    hazard_light: bool = False
    wiper_mode: str = "off"
    warnings: List[str] = field(default_factory=list)

    def apply_can_message(self, frame: CANMessage) -> None:
        if frame.arbitration_id == CANProtocol.RPM_ID:
            self.rpm = CANProtocol.decode_rpm(frame)
        elif frame.arbitration_id == CANProtocol.SPEED_ID:
            self.speed = CANProtocol.decode_speed(frame)
        elif frame.arbitration_id == CANProtocol.FUEL_ID:
            self.fuel = CANProtocol.decode_fuel(frame)
        elif frame.arbitration_id == CANProtocol.LIGHTS_ID:
            lights = CANProtocol.decode_lights(frame)
            self.left_indicator = lights["left"]
            self.right_indicator = lights["right"]
            self.brake_light = lights["brake"]
            self.hazard_light = lights["hazard"]
        elif frame.arbitration_id == CANProtocol.WIPER_ID:
            self.wiper_mode = CANProtocol.decode_wiper(frame)

    def to_dict(self) -> Dict[str, object]:
        return {
            "rpm": self.rpm,
            "speed": self.speed,
            "fuel": self.fuel,
            "left_indicator": self.left_indicator,
            "right_indicator": self.right_indicator,
            "brake_light": self.brake_light,
            "hazard_light": self.hazard_light,
            "wiper_mode": self.wiper_mode,
            "warnings": self.warnings,
        }


class VirtualCockpitController:
    """Thin controller that reflects commands into the dashboard state."""

    def __init__(self) -> None:
        self.state = DashboardState()

    def update_rpm(self, rpm: int) -> None:
        self.state.rpm = max(0, min(rpm, 9000))

    def update_speed(self, speed: int) -> None:
        self.state.speed = max(0, min(speed, 220))

    def update_fuel(self, fuel: int) -> None:
        self.state.fuel = max(0, min(fuel, 100))

    def set_indicator(self, side: str, active: bool) -> None:
        if side == "left":
            self.state.left_indicator = active
        elif side == "right":
            self.state.right_indicator = active
        elif side == "brake":
            self.state.brake_light = active
        elif side == "hazard":
            self.state.hazard_light = active

    def set_wiper_mode(self, mode: str) -> None:
        valid_modes = {"off", "low", "high", "auto"}
        if mode.lower() not in valid_modes:
            raise ValueError(f"Unsupported wiper mode: {mode}")
        self.state.wiper_mode = mode.lower()

    def set_warning(self, message: str) -> None:
        if message not in self.state.warnings:
            self.state.warnings.append(message)

    def get_status(self) -> Dict[str, object]:
        return self.state.to_dict()

    def apply_can_frame(self, frame: CANMessage) -> None:
        self.state.apply_can_message(frame)
