import random
import model
import meta

from database import Config


class Bait:
    def __init__(self, canvas, size, score: 'score for eating', timeout, color):
        self.size = size
        self.half_size = self.size / 2
        self.score = score
        self.timeout = timeout
        self.timer = timeout
        self.canvas = canvas

        self.x = random.randrange(self.half_size, meta.frame_width, self.size)
        self.y = random.randrange(self.half_size, meta.frame_height, self.size)
        self.item = self.canvas.create_rectangle(self.x - self.half_size,
                                                 self.y - self.half_size,
                                                 self.x + self.half_size,
                                                 self.y + self.half_size,
                                                 fill=color)

    def move(self):
        self.timer = self.timeout

        self.x = random.randrange(self.half_size, (meta.frame_width - (self.size + self.half_size)), self.size)
        self.y = random.randrange(self.half_size, (meta.frame_width - (self.size + self.half_size)), self.size)
        model.move(self.canvas, self.item, self.x, self.y)

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

    def __init__(self, user, canvas, size):
        self.body = []
        self.user = user
        self.canvas = canvas
        self.direction = 'stop'
        self.size = size
        self.half_size = self.size / 2  # to don't div every time
        self.start_x = (meta.frame_width / 2) - self.half_size
        self.start_y = (meta.frame_height / 2) - self.half_size
        self.head = self.canvas.create_rectangle(self.start_x - self.half_size,
                                                 self.start_y - self.half_size,
                                                 self.start_x + self.half_size,
                                                 self.start_y + self.half_size,
                                                 fill=Config.fetch(user=self.user, label='Head'))
        self.aims = {
            'stop': None,
            'up': (0, -self.size),
            'down': (0, self.size),
            'left': (-self.size, 0),
            'right': (self.size, 0)
        }

    def move(self):
        aim = self.aims.get(self.direction, None)
        if aim:
            last_pos = model.get_position(self.canvas, self.head)
            self.canvas.move(self.head, *aim)

            for body in self.body:
                temp_pos = model.get_position(self.canvas, body)
                model.move(self.canvas, body, *last_pos)
                last_pos = temp_pos

        self.check_inside()

    def grow(self):
        x, y = model.get_position(self.canvas, self.head)
        aim = self.aims.get(self.direction, None)
        x -= aim[0]
        y -= aim[1]

        self.body.append(
            self.canvas.create_rectangle(x - self.half_size,
                                         y - self.half_size,
                                         x + self.half_size,
                                         y + self.half_size,
                                         fill=Config.fetch(user=self.user, label='Body'))
        )

    def reset(self):
        self.direction = 'stop'
        self.canvas.delete(self.head)
        self.head = self.canvas.create_rectangle(self.start_x - self.half_size,
                                                 self.start_y - self.half_size,
                                                 self.start_x + self.half_size,
                                                 self.start_y + self.half_size,
                                                 fill=Config.fetch(user=self.user, label='Head'))
        for body in self.body:
            self.canvas.delete(body)
        self.body = []

    def set_direction(self, aim):
        if aim in self.aims.keys():
            # if self.direction == 'stop' or aim == 'stop':
            if 'stop' in [self.direction, aim]:  # if snake want to start, or want to stop
                self.direction = aim
            else:
                # if (self.direction == 'up' and aim != 'down') or \
                #    (self.direction == 'down' and aim != 'up') or \
                #    (self.direction == 'left' and aim != 'right') or \
                #    (self.direction == 'right' and aim != 'left'):
                if {self.direction, aim} not in Snake.opposites:
                    self.direction = aim

    def check_inside(self):
        coords = self.canvas.coords(self.head)

        if coords[0] < 0:  # left
            self.canvas.move(self.head, meta.frame_width, 0)
        elif coords[2] > meta.frame_width:  # right
            self.canvas.move(self.head, -meta.frame_width, 0)

        if coords[1] < 0:  # up
            self.canvas.move(self.head, 0, meta.frame_height)
        elif coords[3] > meta.frame_height:  # down
            self.canvas.move(self.head, 0, -meta.frame_height)

    def change_user(self, user):
        if self.user != user:
            self.user = user
            self.change_head_color(Config.fetch(user=self.user, label='Head'))
            self.change_body_color(Config.fetch(user=self.user, label='Body'))

    def change_body_color(self, code):
        Config.update(value=code).where(Config.user == self.user, Config.label == 'Body').execute()

        for body in self.body:
            self.canvas.itemconfig(body, fill=code)

    def change_head_color(self, code):
        Config.update(value=code).where(Config.user == self.user, Config.label == 'Head').execute()

        self.canvas.itemconfig(self.head, fill=code)
