#!/usr/bin/env python3

import pygame
from dataclasses import dataclass


@dataclass
class PelcoD:
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


def main():
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()

    if pygame.joystick.get_count() == 0:
        print("No controller found")
        pygame.quit()
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    wide = False
    done = False

    while not done:

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == 2:
                done = True

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

        if left or right or up or down:
            pan_speed = int(39 * abs(horizontal))
            tilt_speed = int(39 * abs(vertical))
        else:
            pan_speed = 0
            tilt_speed = 0

        pelco = PelcoD(
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
        print(pelco.message.hex(" "))
        clock.tick(137)

    pygame.quit()


if __name__ == "__main__":
    main()
