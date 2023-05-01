import random

import model
import meta


class Bait:
    def __init__(self, canvas, energy, timeout, color, size=meta.UNIT_SIZE):
        self.canvas = canvas
        self.energy = energy
        self.timeout = timeout
        self.timer = timeout
        self.size = size
        self.half_size = self.size / 2

        self.x, self.y = self.get_random_pos()
        self.item = self.canvas.create_rectangle(self.x - self.half_size,
                                                 self.y - self.half_size,
                                                 self.x + self.half_size,
                                                 self.y + self.half_size,
                                                 fill=color)

    def move(self):
        self.timer = self.timeout
        self.x, self.y = self.get_random_pos()
        model.move(self.canvas, self.item, self.x, self.y)

    def get_random_pos(self):
        return (
            random.randrange(self.half_size, meta.CANVAS_WIDTH, self.size),
            random.randrange(self.half_size, meta.CANVAS_HEIGHT, self.size)
        )

    def reset(self):
        self.move()

    def auto_move(self):
        """ move when time is over """

        if self.timer:
            self.timer -= 1
        else:
            self.move()


class Snake:
    opposites = [
        {'up', 'down'},
        {'left', 'right'}
    ]

    def __init__(self, canvas, size=meta.UNIT_SIZE, head_color='black', body_color='gray'):
        self.body = []
        self.canvas = canvas
        self.last_direction = 'up'
        self.direction = 'up'
        self.size = size
        self.head_color = head_color
        self.body_color = body_color
        self.half_size = self.size / 2  # to don't div every time
        self.start_x = meta.CANVAS_WIDTH / 2  # for odd N
        self.start_y = meta.CANVAS_HEIGHT / 2
        self.head = self.create_quad(self.start_x, self.start_y, color=self.head_color)
        self.aims = {
            'up': (0, -self.size),
            'down': (0, self.size),
            'left': (-self.size, 0),
            'right': (self.size, 0)
        }

    def move(self):
        self.last_direction = self.direction
        aim = self.aims[self.direction]
        last_pos = model.get_position(self.canvas, self.head)
        self.canvas.move(self.head, *aim)

        for body in self.body:
            temp_pos = model.get_position(self.canvas, body)
            model.move(self.canvas, body, *last_pos)
            last_pos = temp_pos

        self.check_inside()

    def grow(self):
        aim = self.aims[self.direction]
        x, y = model.get_position(self.canvas, self.head)
        x -= aim[0]
        y -= aim[1]

        self.body.append(self.create_quad(x, y, color=self.body_color))

    def reset(self):
        self.direction = 'up'
        self.last_direction = 'up'
        self.canvas.delete(self.head)
        self.head = self.create_quad(self.start_x, self.start_y, color=self.head_color)
        for body in self.body:
            self.canvas.delete(body)
        self.body = []

    def create_quad(self, x, y, color=None):
        return self.canvas.create_rectangle(
            x - self.half_size,
            y - self.half_size,
            x + self.half_size,
            y + self.half_size,
            fill=color
        )

    def set_direction(self, direction):
        if direction in self.aims.keys():
            if {self.last_direction, direction} not in Snake.opposites:
                self.direction = direction

    def check_inside(self):
        coords = self.canvas.coords(self.head)

        if coords[0] < 0:  # left
            self.canvas.move(self.head, meta.CANVAS_WIDTH, 0)
        elif coords[2] > meta.CANVAS_WIDTH:  # right
            self.canvas.move(self.head, -meta.CANVAS_WIDTH, 0)

        if coords[1] < 0:  # up
            self.canvas.move(self.head, 0, meta.CANVAS_HEIGHT)
        elif coords[3] > meta.CANVAS_HEIGHT:  # down
            self.canvas.move(self.head, 0, -meta.CANVAS_HEIGHT)

    def change_body_color(self, code):
        self.body_color = code
        for body in self.body:
            self.canvas.itemconfig(body, fill=self.body_color)

    def change_head_color(self, code):
        self.head_color = code
        self.canvas.itemconfig(self.head, fill=self.head_color)
