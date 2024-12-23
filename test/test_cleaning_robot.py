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

    @patch.object(IBS, "get_charge_left")
    def test_execute_command_forward(self, mock_ibs: Mock):
        mock_ibs.return_value = 11
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        self.assertEqual("(0,1,N)", cr.execute_command("f"))

    @patch.object(IBS, "get_charge_left")
    def test_execute_command_right(self, mock_ibs: Mock):
        mock_ibs.return_value = 100
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        self.assertEqual("(0,0,E)", cr.execute_command("r"))

    @patch.object(IBS, "get_charge_left")
    def test_execute_command_left(self, mock_ibs: Mock):
        mock_ibs.return_value = 50
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 1
        cr.pos_y = 0
        self.assertEqual("(1,0,W)", cr.execute_command("l"))

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

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "input")
    def test_obstacle_in_front_of_robot(self, mock_infrared_sensor: Mock, mock_ibs: Mock):
        mock_infrared_sensor.return_value = True
        mock_ibs.return_value = 20
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        self.assertEqual("(0,0,N)(0,1)", cr.execute_command("f"))

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "input")
    def test_no_obstacle_in_front_of_robot(self, mock_infrared_sensor: Mock, mock_ibs: Mock):
        mock_ibs.return_value = 11
        mock_infrared_sensor.return_value = False
        cr = CleaningRobot()
        cr.heading = "N"
        cr.pos_x = 0
        cr.pos_y = 0
        self.assertEqual("(0,1,N)", cr.execute_command("f"))

    @patch.object(IBS, "get_charge_left")
    def test_execute_command_not_enough_battery(self, mock_ibs: Mock):
        mock_ibs.return_value = 10
        cr = CleaningRobot()
        cr.heading = "E"
        cr.pos_x = 1
        cr.pos_y = 1
        self.assertEqual("!(1,1,E)", cr.execute_command("f"))

    def test_set_borders(self):
        cr = CleaningRobot()
        self.assertEqual(cr.set_borders(0, 5, 0, 5), "B(0,5,0,5)", "Borders were not set")

    def test_get_borders(self):
        cr = CleaningRobot()
        cr.set_borders(0, 5, 0, 5)
        self.assertEqual(cr.get_borders(), "B(0,5,0,5)", "Borders were not got correctly")

    def test_default_borders(self):
        cr = CleaningRobot()
        self.assertEqual(cr.get_borders(), "B(0,9,0,9)", "Default borders were not retrieved correctly")

    @patch.object(GPIO, "output")
    def test_robot_status_out_of_borders(self, warning_led: Mock):
        cr = CleaningRobot()
        cr.pos_x = 10
        cr.pos_y = 3
        cr.heading = "N"

        self.assertEqual(cr.robot_status(), "O(10,3,N)", "Status was not returned properly")
        warning_led.assert_called_with(11, True)
        self.assertTrue(cr.warning_led_on, "Warning LED should be on when out of borders")

    @patch.object(GPIO, "output")
    def test_robot_status_within_borders(self, warning_led: Mock):
        cr = CleaningRobot()
        cr.pos_x = 9
        cr.pos_y = 9
        cr.heading = "N"

        self.assertEqual(cr.robot_status(), "(9,9,N)", "Status was not returned properly")
        warning_led.assert_called_with(11, False)
        self.assertFalse(cr.warning_led_on, "Warning LED should be off when within borders")

    @patch.object(IBS, "get_charge_left")
    def test_execute_command_out_of_borders(self, mock_ibs: Mock):
        mock_ibs.return_value = 11
        cr = CleaningRobot()
        cr.pos_x = 10
        cr.pos_y = 1
        cr.heading = "N"
        self.assertEqual(cr.execute_command("f"), "O(10,1,N)", "Status was not returned properly")
