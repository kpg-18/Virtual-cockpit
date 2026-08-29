import unittest

from can_protocol import CANMessage, CANProtocol
from dashboard_simulator import VirtualCockpitController


class WiperControlTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = VirtualCockpitController()

    def test_wiper_off_by_default(self):
        self.assertEqual(self.controller.get_status()["wiper_mode"], "off")

    def test_wiper_low_mode(self):
        self.controller.set_wiper_mode("low")
        self.assertEqual(self.controller.get_status()["wiper_mode"], "low")

    def test_wiper_high_mode(self):
        self.controller.set_wiper_mode("high")
        self.assertEqual(self.controller.get_status()["wiper_mode"], "high")

    def test_wiper_auto_mode(self):
        self.controller.set_wiper_mode("auto")
        self.assertEqual(self.controller.get_status()["wiper_mode"], "auto")

    def test_invalid_mode_raises_error(self):
        with self.assertRaises(ValueError):
            self.controller.set_wiper_mode("turbo")

    def test_dashboard_speed_and_rpm_are_clamped(self):
        self.controller.update_speed(500)
        self.controller.update_rpm(15000)
        self.assertEqual(self.controller.get_status()["speed"], 220)
        self.assertEqual(self.controller.get_status()["rpm"], 9000)

    def test_indicator_flags_toggle(self):
        self.controller.set_indicator("left", True)
        self.controller.set_indicator("right", True)
        self.controller.set_indicator("hazard", True)
        status = self.controller.get_status()
        self.assertTrue(status["left_indicator"])
        self.assertTrue(status["right_indicator"])
        self.assertTrue(status["hazard_light"])

    def test_ecu_can_messages_update_dashboard_state(self):
        rpm_msg = CANProtocol.encode_rpm(4200)
        speed_msg = CANProtocol.encode_speed(65)
        fuel_msg = CANProtocol.encode_fuel(55)
        light_msg = CANProtocol.encode_lights(True, False, True, True)
        wiper_msg = CANProtocol.encode_wiper("auto")

        self.controller.apply_can_frame(rpm_msg)
        self.controller.apply_can_frame(speed_msg)
        self.controller.apply_can_frame(fuel_msg)
        self.controller.apply_can_frame(light_msg)
        self.controller.apply_can_frame(wiper_msg)

        status = self.controller.get_status()
        self.assertEqual(status["rpm"], 4200)
        self.assertEqual(status["speed"], 65)
        self.assertEqual(status["fuel"], 55)
        self.assertTrue(status["left_indicator"])
        self.assertTrue(status["brake_light"])
        self.assertTrue(status["hazard_light"])
        self.assertEqual(status["wiper_mode"], "auto")

    def test_brake_light_can_be_controlled_like_an_ecu_signal(self):
        self.controller.set_indicator("brake", True)
        self.assertTrue(self.controller.get_status()["brake_light"])

        self.controller.set_indicator("brake", False)
        self.assertFalse(self.controller.get_status()["brake_light"])


if __name__ == "__main__":
    unittest.main()
