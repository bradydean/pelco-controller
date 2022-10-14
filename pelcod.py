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
