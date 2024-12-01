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

    def test_execute_command_invalid_option(self):
        cr = CleaningRobot()
        self.assertRaises(CleaningRobotError, cr.execute_command, "j")

    def test_execute_command_forward(self):
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        cr.execute_command("f")
        self.assertEqual("(0,1,N)", cr.robot_status())

    def test_execute_command_right(self):
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        cr.execute_command("r")
        self.assertEqual("(0,0,E)", cr.robot_status())

    def test_execute_command_left(self):
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 1
        cr.pos_y = 0
        cr.execute_command("l")
        self.assertEqual("(1,0,W)", cr.robot_status())

    @patch.object(GPIO, "input")
    def test_obstacle_found(self, mock_infrared_sensor: Mock):
        mock_infrared_sensor.return_value = True
        cr = CleaningRobot()
        self.assertTrue(cr.obstacle_found())

    @patch.object(GPIO, "input")
    def test_obstacle_was_not_found(self, mock_infrared_sensor: Mock):
        mock_infrared_sensor.return_value = False
        cr = CleaningRobot()
        self.assertFalse(cr.obstacle_found())

    @patch.object(GPIO, "input")
    def test_obstacle_in_front_of_robot(self, mock_infrared_sensor: Mock):
        mock_infrared_sensor.return_value = True
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        cr.execute_command("f")
        self.assertEqual("(0,0,N)(0,1)", cr.robot_status())

    @patch.object(GPIO, "input")
    def test_no_obstacle_in_front_of_robot(self, mock_infrared_sensor: Mock):
        mock_infrared_sensor.return_value = False
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        cr.execute_command("f")
        self.assertEqual("(0,1,N)", cr.robot_status())
