#!/usr/bin/env python3
from os import environ

from serial import SerialException

from controller import Controller

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import sys
import pygame
import serial
import argparse


def main(device):
    pygame.init()

    if pygame.joystick.get_count() == 0:
        print("No controller found")
        pygame.quit()
        sys.exit(1)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    try:
        camera = serial.Serial(device)
    except SerialException as e:
        print(f"Couldn't get serial device: {e}")
        sys.exit(1)

    controller = Controller(joystick=joystick, camera=camera)
    controller.run()
    pygame.quit()
    camera.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pelco D controller")
    parser.add_argument("device", help="Device path or COM port")
    args = parser.parse_args()
    main(args.device)
