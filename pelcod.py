#!/usr/bin/env python3
from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import sys
import pygame
import serial
import argparse

from dataclasses import dataclass


@dataclass
class PelcoDMovement:
    """1: addr 0xFF
    2: addr
    3: cmd1 (command extension)
    4: cmd2 (basic command)
    5: data1 (pan speed, 0x00-0x40)
    6: data2 (tilt speed, 0x00-0x40)
    7: checksum (sum 2-6) % 255"""

    addr: int
    zoom_wide: bool
    zoom_tele: bool
    up: bool
    down: bool
    left: bool
    right: bool
    pan_speed: int
    tilt_speed: int

    ZOOM_WIDE = 1 << 6
    ZOOM_TELE = 1 << 5
    DOWN = 1 << 4
    UP = 1 << 3
    LEFT = 1 << 2
    RIGHT = 1 << 1

    @property
    def message(self):
        cmd1 = 0x00
        cmd2 = 0x00

        if self.zoom_tele:
            cmd2 |= self.ZOOM_TELE
        elif self.zoom_wide:
            cmd2 |= self.ZOOM_WIDE

        if self.up:
            cmd2 |= self.UP

        if self.down:
            cmd2 |= self.DOWN

        if self.right:
            cmd2 |= self.RIGHT

        if self.left:
            cmd2 |= self.LEFT

        data1 = self.pan_speed
        data2 = self.tilt_speed

        data = bytes([self.addr, cmd1, cmd2, data1, data2])
        checksum = sum(data) % 255
        return bytes([0xFF]) + data + bytes([checksum])


def main(device):
    pygame.init()
    clock = pygame.time.Clock()

    if pygame.joystick.get_count() == 0:
        print("No controller found")
        pygame.quit()
        sys.exit(1)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    camera = serial.Serial(device)

    wide = False
    done = False

    should_quit = False
    should_move = False
    should_print = False

    while not done:

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == 3:
                should_quit = True
            elif event.type == pygame.JOYAXISMOTION:
                should_move = True
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 2:
                should_print = True

        if should_quit:
            done = True
        elif should_print:
            print("hello")
        elif should_move:
            horizontal = joystick.get_axis(0)
            vertical = joystick.get_axis(1)
            zoom_tele = joystick.get_axis(5)
            zoom_wide = joystick.get_axis(2)

            left = abs(horizontal) > 0.1 and horizontal < 0
            right = abs(horizontal) > 0.1 and horizontal > 0
            up = abs(vertical) > 0.1 and vertical < 0
            down = abs(vertical) > 0.1 and vertical > 0

            tele = not wide and zoom_tele > -1 + 0.01
            wide = not tele and zoom_wide > -1 + 0.01

            if left or right or up or down or tele or wide:
                if left or right:
                    pan_speed = int(0x39 * abs(horizontal))
                else:
                    pan_speed = 0

                if up or down:
                    tilt_speed = int(0x39 * abs(vertical))
                else:
                    tilt_speed = 0

                pelco = PelcoDMovement(
                    addr=1,
                    up=up,
                    down=down,
                    left=left,
                    right=right,
                    zoom_wide=wide,
                    zoom_tele=tele,
                    pan_speed=pan_speed,
                    tilt_speed=tilt_speed,
                )
                message = pelco.message
                print(message.hex(" "))
                camera.write(message)

        should_move = False
        should_quit = False
        should_print = False

        clock.tick(137)

    pygame.quit()
    camera.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pelco D controller")
    parser.add_argument("device", help="Device path or COM port")
    args = parser.parse_args()
    main(args.device)
