# Virtual Cockpit Control Project

This project simulates a vehicle virtual cockpit built around a CAN-style communication layer. It demonstrates how dashboard values such as RPM, vehicle speed, fuel level, and indicator lights can be controlled and monitored in a way that mirrors ADAS and embedded automotive workflows.

## Features

- CAN message protocol model for dashboard telemetry
- Virtual cockpit dashboard with live indicators
- Wiper control states: Off, Low, High, and Auto
- Test case definitions for manual and automated validation
- Easy Python-only setup with no external dependencies

## Project structure

- `app.py` – HTTP dashboard and API
- `can_protocol.py` – CAN message encoding and decoding
- `dashboard_simulator.py` – dashboard state management
- `tests/test_wiper_cases.py` – automated wiper validation tests
- `static/` – dashboard UI assets

## Run locally

```bash
cd /Users/kruparthprakashgowda/Documents/virtual-cockpit
python3 app.py
```

Then open http://localhost:8000

## Example CAN messages

- RPM: `0x101`
- Speed: `0x102`
- Fuel: `0x103`
- Light status: `0x104`
- Wiper state: `0x105`

## Wiper validation

The project includes both manual test cases and automated test assertions to validate:

- wiper OFF state
- low-speed system operation
- high-speed operation
- auto mode activation
- indicator relationship checks

## Notes

This is a simulation designed for learning, validation, and demonstration purposes. It is structured to reflect realistic automotive control workflows and test planning in a virtual environment.
