import pygame

from dataclasses import dataclass, field
from serial import Serial
from pelcod import PelcoDMovement


@dataclass
class Controller:
    joystick: pygame.joystick.Joystick
    camera: Serial
    command: bytes = field(default_factory=bytes)
    clock: pygame.time.Clock = field(default_factory=pygame.time.Clock)
    done: bool = False

    wide: bool = False
    tele: bool = False
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    pan_speed: int = 0
    tilt_speed: int = 0

    horizontal: float = 0.0
    vertical: float = 0.0
    zoom_tele: float = 0.0
    zoom_wide: float = 0.0

    frame_rate: int = 137
    should_move: bool = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and event.button == 3:
                self.done = True
            elif event.type == pygame.JOYAXISMOTION:
                self.should_move = True

    def get_controller_state(self):
        self.horizontal = self.joystick.get_axis(0)
        self.vertical = self.joystick.get_axis(1)
        self.zoom_tele = self.joystick.get_axis(5)
        self.zoom_wide = self.joystick.get_axis(2)

    def determine_motion(self):
        self.left = abs(self.horizontal) > 0.1 and self.horizontal < 0
        self.right = abs(self.horizontal) > 0.1 and self.horizontal > 0
        self.up = abs(self.vertical) > 0.1 and self.vertical < 0
        self.down = abs(self.vertical) > 0.1 and self.vertical > 0
        self.tele = not self.wide and self.zoom_tele > -1 + 0.01
        self.wide = not self.tele and self.zoom_wide > -1 + 0.01

    def should_issue_command(self):
        return any([self.left, self.right, self.up, self.down, self.tele, self.wide])

    def determine_speed(self):
        if self.left or self.right:
            self.pan_speed = int(0x39 * abs(self.horizontal))
        else:
            self.pan_speed = 0

        if self.up or self.down:
            self.tilt_speed = int(0x39 * abs(self.vertical))
        else:
            self.tilt_speed = 0

    def construct_command(self):
        self.command = PelcoDMovement(
            addr=1,
            up=self.up,
            down=self.down,
            left=self.left,
            right=self.right,
            zoom_wide=self.wide,
            zoom_tele=self.tele,
            pan_speed=self.pan_speed,
            tilt_speed=self.tilt_speed,
        ).message

    def print_command(self):
        print(self.command.hex(" "))

    def issue_command(self):
        self.camera.write(self.command)

    def update_state(self):
        if self.should_move:
            self.get_controller_state()
            self.determine_motion()
            if self.should_issue_command():
                self.determine_speed()
                self.construct_command()
                self.print_command()
                self.issue_command()

    def clear_flags(self):
        self.should_move = False

    def tick(self):
        self.clock.tick(self.frame_rate)

    def run(self):
        while not self.done:
            self.handle_events()
            self.update_state()
            self.clear_flags()
            self.tick()