from unittest import TestCase

from src.cleaning_robot import CleaningRobot, CleaningRobotError


class TestCleaningRobot(TestCase):

    # @patch.object(GPIO, "input")
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
