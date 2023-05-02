import sys
import os

from database import User
import model


IS_WINDOWS = (sys.platform == 'win32')
SECRET_FOLDER = os.path.expanduser(r'~\.SnakeTk')
if not os.path.exists(SECRET_FOLDER):
    os.mkdir(SECRET_FOLDER)

TITLE = 'Snake Game'
ICON_PATH = r'icon.ico'

WIDTH = 520
HEIGHT = 635
UNIT_SIZE = 16
CANVAS_WIDTH_N = 31  # number of pixels
CANVAS_HEIGHT_N = 31  # must be odd
CANVAS_WIDTH = CANVAS_WIDTH_N * UNIT_SIZE
CANVAS_HEIGHT = CANVAS_HEIGHT_N * UNIT_SIZE

BASE_ENERGY = 200

FONTS = {
    'medium': ('Segoe ui', 15),
    'large': ('Segoe ui', 20),
    'large_italic': ('Segoe ui', 20, 'italic'),
}

LINKS = {
    'telegram': 'https://t.me/sina_programer',
    'github': 'https://github.com/sina-programer'
}


UNWANTED_BINDINGS = (
    'cut',
    'delete',
    'edit_cell',
    'edit_header',
    'right_click_popup_menu',
    'rc_insert_column',
    'rc_delete_column',
    'rc_insert_row',
    'rc_delete_row',
    'column_drag_and_drop',
    'row_drag_and_drop',
    'double_click_row_resize',
    'row_height_resize',
    'column_height_resize',
    'row_width_resize',
)


defaults = {
    'username': 'Player',
    'password': '',
}


default_user = User.get_or_none(username=defaults['username'])
if not default_user:
    default_user = model.create_user(username=defaults['username'], password=defaults['password'], is_default=True)
