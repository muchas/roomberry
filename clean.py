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


def turn_right(robot, radians, velocity=20):
    radius = 150  # 15 cm
    distance = radians / radius
    duration = abs(distance / velocity)
    robot.drive(int(math.copysign(velocity, distance)), DRIVE.TURN_IN_PLACE_CW)
    sleep(duration)
    robot.drive(0, 0)


# 20 mm per second (2 cm/s)
def drive_straight(robot, distance, velocity=20):
    duration = abs(distance / velocity)
    robot.logger.info("driving straight for {} seconds with {} mm/s".format(duration, velocity))
    robot.drive_straight(int(math.copysign(velocity, distance)))
    sleep(duration) 
    robot.drive_straight(0)


def main():
    # add methods to turn logging to console on/off
    logger = _configure_logger()

    port = '/dev/serial0'
    brc_pin = 0
    
    try:
        robot = Create2(port, brc_pin)
        robot.oi_mode = MODES.SAFE

        drive_straight(robot, -1000)  # move back 100 cm
        turn_right(robot, 0.785)  # turn right by 90 degrees
        drive_straight(4000)  # move 400 cm forward

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
