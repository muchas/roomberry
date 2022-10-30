import math
import logging

from sys import stdout
from time import sleep

from irobot.robots.create2 import Create2, RobotConnectionError, ModeChangeError
from irobot.openinterface.constants import MODES, DRIVE, RAW_LED


def _configure_logger():
    class Formatter(logging.Formatter):
        def __init__(self, fmt):
            logging.Formatter.__init__(self, fmt)

        def format(self, record):
            msg = logging.Formatter.format(self, record)
            lines = msg.split('\n')
            return '{0}\n{1}'.format(
                lines[0],
                '\n'.join(['\t{0}'.format(line) for line in lines[1:]]))

    logger = logging.getLogger('Create2')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(Formatter('%(levelname)s\n%(message)s'))
    logger.addHandler(ch)
    logger.disabled = False

    return logger


def turn_right(robot, radians, velocity=100):
    radius = 100  # 10 cm
    distance = radius * radians
    duration = abs(distance / velocity)
    robot.logger.info("turning right for {} seconds with {} mm/s".format(duration, velocity))
    robot.drive(int(math.copysign(velocity, distance)), DRIVE.TURN_IN_PLACE_CW)
    sleep(duration)
    robot.drive(0, 0)


def turn_left(robot, radians, velocity=100):
    radius = 100  # 10 cm
    distance = radius * radians
    duration = abs(distance / velocity)
    robot.logger.info("turning right for {} seconds with {} mm/s".format(duration, velocity))
    robot.drive(int(math.copysign(velocity, distance)), DRIVE.TURN_IN_PLACE_CCW)
    sleep(duration)
    robot.drive(0, 0)


# 20 mm per second (2 cm/s)
def drive_straight(robot, distance, velocity=200):
    duration = abs(distance / velocity)
    robot.logger.info("driving straight for {} seconds with {} mm/s".format(duration, velocity))
    robot.drive_straight(int(math.copysign(velocity, distance)))
    sleep(duration) 
    robot.drive_straight(0)


def drive_straight_until_wall(robot, velocity=160):
    hit_wall = False
    while not hit_wall:
        robot.drive_straight(velocity)
        sleep(0.2)
        light_bumper = robot.light_bumper
        hit_wall = any((light_bumper.left, light_bumper.center_left, light_bumper.center_right, light_bumper.right))
    robot.drive_straight(0)


def main():
    # add methods to turn logging to console on/off
    logger = _configure_logger()

    port = '/dev/serial0'
    brc_pin = 0
    
    try:
        robot = Create2(port, brc_pin)
        robot.oi_mode = MODES.SAFE

        drive_straight(robot, -1100)  # move back 110 cm
        turn_right(robot, math.pi / 2)  # turn right by 90 degrees
        drive_straight_until_wall(robot)

        drive_straight(robot, -110)  # move back 11 cm
        turn_right(robot, math.pi / 2 + 0.05)
        drive_straight_until_wall(robot)

        drive_straight(robot, -60) # move back 6 cm
        turn_right(robot, math.pi)

        drive_straight(robot, 1800) # move forward 180 ccm
        turn_left(robot, math.pi / 2)

        drive_straight(robot, 3000)  # move forward 300 cm
        robot.seek_dock()

        robot.oi_mode = MODES.PASSIVE
        robot.close()

    except RobotConnectionError as e:
        print(e, '\nInner Exception:', e.__cause__)
        return
    except ModeChangeError:
        print('Failed to enter Passive mode')
        return

if __name__ == "__main__":
    main()
