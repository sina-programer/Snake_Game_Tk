import sys
import os

from database import User, Config


is_windows = (sys.platform == 'win32')
secret_folder = os.path.expanduser(r'~\.SnakeTk')
if not os.path.exists(secret_folder):
    os.mkdir(secret_folder)

title = 'Snake Game'
icon_path = r'icon.ico'

main_width = 540
main_height = 610
frame_width = 512  # frame for moving snake
frame_height = 480

base_energy = 200
best_scores_limit = 20

medium_font = ('Segoe ui', 15)
large_font = ('Segoe ui', 20)
large_font_italic = ('Segoe ui', 20, 'italic')

links = {
    'telegram': 'https://t.me/sina_programer',
    'github': 'https://github.com/sina-programer'
}


unwanted_bindings = (
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
    'double_click_column_resize',
    'column_width_resize'
)

default_level = 2
default_username = 'Player_1'
default_colors = {
    'Head': '#000000',
    'Body': '#A9A9A9',
    'Background': '#ADD8E6'
}


default_user, created = User.get_or_create(username=default_username, password='')
if created:
    for ctype, color in default_colors.items():
        Config.create(user=default_user, label=ctype, value=color)
