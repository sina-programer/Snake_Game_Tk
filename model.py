from tkinter import messagebox
import tkinter as tk
import datetime as dt
import time

from database import User, Score, Config
import meta


def create_user(username, password):
    user = User.create(username=username, password=password, signup_date=dt.datetime.now())
    for label, value in meta.defaults['configs'].items():
        Config.create(user=user, label=label, value=value)

    return user


def check_collision(canvas, obj1, obj2):
    """ This func get two objects & check their collision """

    crd_a = canvas.coords(obj1)
    crd_b = canvas.coords(obj2)

    if (crd_a[0] <= crd_b[0] < crd_a[2] or crd_a[0] < crd_b[2] <= crd_a[2]) and \
       (crd_a[1] <= crd_b[1] < crd_a[3] or crd_a[1] < crd_b[3] <= crd_a[3]):
        return True

    return False


def get_position(canvas, item):
    """ return center position of item """

    coords = canvas.coords(item)
    return ((coords[2] - coords[0]) / 2) + coords[0], \
           ((coords[3] - coords[1]) / 2) + coords[1]


def get_coords(x, y, size):
    """ return coords of an object from center & size """

    half_size = size / 2
    return [
        x - half_size,
        y - half_size,
        x + half_size,
        y + half_size
    ]


def move(canvas, item, x, y):
    """ give an object, then first move to 0-0 after to x-y """

    item_pos = get_position(canvas, item)
    canvas.move(item, -item_pos[0], -item_pos[1])
    canvas.move(item, x, y)
