from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot, CleaningRobotError


class TestCleaningRobot(TestCase):

    def test_position_x_after_initialize(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        self.assertEqual(0, cr.pos_x, "Position x was not set properly during initialization")

    def test_position_y_after_initialize(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        self.assertEqual(0, cr.pos_y, "Position y was not set properly during initialization")

    def test_heading_after_initialize(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        self.assertEqual("N", cr.heading, "Heading was not set properly during initialization")

    def test_current_status_first_option(self):
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        self.assertEqual("(0,0,N)", cr.robot_status(), "Status was not written properly")

    def test_current_status_second_option(self):
        cr = CleaningRobot()
        cr.heading = "S"
        cr.pos_x = 2
        cr.pos_y = 2
        self.assertEqual("(2,2,S)", cr.robot_status(), "Status was not written properly")

    def test_current_status_invalid_option(self):
        cr = CleaningRobot()
        cr.heading = "J"
        cr.pos_x = 2
        cr.pos_y = 2
        self.assertRaises(CleaningRobotError, cr.robot_status)

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_manage_cleaning_system_enough_battery(self, mock_ibs: Mock, mock_output: Mock):
        mock_ibs.return_value = 11
        cr = CleaningRobot()
        cr.manage_cleaning_system()
        mock_output.assert_has_calls([call(cr.CLEANING_SYSTEM_PIN, True),
                                      call(cr.RECHARGE_LED_PIN, False)])
        self.assertTrue(cr.cleaning_system_on)
        self.assertFalse(cr.recharge_led_on)

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_manage_cleaning_system_not_enough_battery(self, mock_ibs: Mock, mock_output: Mock):
        mock_ibs.return_value = 10
        cr = CleaningRobot()
        cr.manage_cleaning_system()
        mock_output.assert_has_calls([call(cr.CLEANING_SYSTEM_PIN, False),
                                      call(cr.RECHARGE_LED_PIN, True)])
        self.assertFalse(cr.cleaning_system_on)
        self.assertTrue(cr.recharge_led_on)
