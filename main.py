#!/usr/bin/env python3

from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import sys
import pygame
import pygame_gui
import serial
import argparse

from controller import Controller, ElementContainer


def main(device):
    pygame.init()
    pygame.display.set_caption("Pelco D Controller")

    if pygame.joystick.get_count() == 0:
        print("No controller found")
        pygame.quit()
        sys.exit(1)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    try:
        camera = serial.Serial(device)
    except serial.SerialException as e:
        print(f"Couldn't get serial device: {e}")
        sys.exit(1)

    window = pygame.display.set_mode((800, 600))
    manager = pygame_gui.UIManager((800, 600))

    elements = ElementContainer(
        fps=pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((0, 0), (45, 40)),
            manager=manager,
        ),
        command=pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((60, 0), (180, 40)),
            manager=manager,
        ),
    )

    controller = Controller(
        joystick=joystick,
        camera=camera,
        window=window,
        ui_manager=manager,
        elements=elements,
    )
    controller.run()
    pygame.quit()
    camera.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pelco D controller")
    parser.add_argument("device", help="Device path or COM port")
    args = parser.parse_args()
    main(args.device)
