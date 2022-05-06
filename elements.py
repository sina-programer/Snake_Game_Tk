import random
import model
import meta


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