from database import User, Color

import sys
is_windows = sys.platform == 'win32'

title = 'Snake Game'
icon_path = r'Files\icon.ico'

main_width = 540
main_height = 610
frame_width = 512  # frame for moving snake
frame_height = 480

base_energy = 200
best_scores_limit = 20

medium_font = ('Segoe ui', 15)
large_font = ('Segoe ui', 20)
large_font_italic = ('Segoe ui', 20, 'italic')

default_level = 2
default_username = 'Player_1'
default_colors = {
    'Head': '#000000',
    'Body': '#A9A9A9',
    'Background': '#ADD8E6'
}

links = {
    'github': 'https://github.com/sina-programer',
    'telegram': 'https://t.me/sina_programer'
}

default_user, create = User.get_or_create(username=default_username, password='')
if create:
    for ctype, color in default_colors.items():
        Color.create(user=default_user, code=color, type=ctype)
