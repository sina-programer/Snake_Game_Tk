from tkinter import messagebox
import tkinter as tk
import datetime as dt
import time

from database import User, Score, Color
from elements import Bait
from snake import Snake
import dialogs
import meta


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
    return ((coords[2] - coords[0]) / 2) + coords[0], ((coords[3] - coords[1]) / 2) + coords[1]


def move(canvas, item, x, y):
    """ give an object, then first move to 0-0 after to x-y """

    item_pos = get_position(canvas, item)
    canvas.move(item, -item_pos[0], -item_pos[1])
    canvas.move(item, x, y)


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.menus = {}
        self.delay = None
        self.canvas = None
        self.user = meta.default_user

        self.score = tk.IntVar()
        self.level = tk.IntVar()
        self.energy = tk.IntVar()
        self.best_score = tk.IntVar()

        self.master = master
        self.master.config(menu=self.init_menu())


        labels_frame = tk.Frame(self.master)
        score_frame = tk.Frame(labels_frame)
        bestscore_frame = tk.Frame(labels_frame)
        username_frame = tk.Frame(labels_frame)
        level_frame = tk.Frame(labels_frame)
        energy_frame = tk.Frame(labels_frame)

        labels_frame.pack(pady=20)
        score_frame.grid(row=1, column=1, padx=15)
        bestscore_frame.grid(row=2, column=1, padx=15)
        username_frame.grid(row=1, column=2, padx=15, rowspan=2)
        level_frame.grid(row=1, column=3, padx=15)
        energy_frame.grid(row=2, column=3, padx=15)

        tk.Label(score_frame, text='Score:', font=meta.medium_font).pack(side=tk.LEFT, padx=5)
        tk.Label(score_frame, textvariable=self.score, font=meta.medium_font).pack(side=tk.RIGHT)

        tk.Label(bestscore_frame, text='Best Score:', font=meta.medium_font).pack(side=tk.LEFT, padx=5)
        tk.Label(bestscore_frame, textvariable=self.best_score, font=meta.medium_font).pack(side=tk.RIGHT)

        tk.Label(username_frame, text='User:', font=meta.large_font).pack(side=tk.LEFT, padx=5)
        self.username_lbl = tk.Label(username_frame, text=self.user.username, font=meta.large_font_italic)
        self.username_lbl.pack(side=tk.RIGHT)

        tk.Label(level_frame, text='Level:', font=meta.medium_font).pack(side=tk.LEFT, padx=5)
        tk.Label(level_frame, textvariable=self.level, font=meta.medium_font).pack(side=tk.RIGHT)

        tk.Label(energy_frame, text='Energy:', font=meta.medium_font).pack(side=tk.LEFT, padx=5)
        tk.Label(energy_frame, textvariable=self.energy, font=meta.medium_font).pack(side=tk.RIGHT)


        self.canvas = tk.Canvas(self, width=meta.frame_width, height=meta.frame_height,
                                highlightthickness=1.5, highlightbackground='black')
        self.snake = Snake(self.user, self.canvas, size=16)
        self.bait = Bait(self.canvas, size=16, score=30, timeout=60, color='green')
        self.set_level(meta.default_level)
        self.update_personalizations()


        self.master.bind('<Up>', lambda _: self.snake.set_direction('up'))
        self.master.bind('<Down>', lambda _: self.snake.set_direction('down'))
        self.master.bind('<Left>', lambda _: self.snake.set_direction('left'))
        self.master.bind('<Right>', lambda _: self.snake.set_direction('right'))
        self.master.bind('<Escape>', lambda _: self.snake.set_direction('stop'))

        self.pack(side=tk.BOTTOM, pady=5)
        self.canvas.pack(pady=5)

        self.game_loop()

    def restart(self):
        if score := self.score.get():  # auto save score when change level meanwhile game loop
            Score.create(user=self.user, score=score,
                         level=self.level.get(), datetime=dt.datetime.now())

        if score > self.best_score.get():
            self.best_score.set(score)

        self.energy.set(meta.base_energy)
        self.score.set(0)
        self.snake.reset()
        self.bait.reset()

    def change_user(self, user):
        self.user = user
        self.username_lbl.config(text=self.user.username)
        self.snake.change_user(self.user)  # change colors too
        self.update_personalizations()

        if self.user == meta.default_user:
            self.menus['account'].entryconfig('Manage Account', state=tk.DISABLED)
        else:
            self.menus['account'].entryconfig('Manage Account', state=tk.NORMAL)

    def update_personalizations(self):
        self.canvas.config(bg=Color.get(user=self.user, type='Background').code)
        self.snake.change_head_color(Color.get(user=self.user, type='Head').code)
        self.snake.change_body_color(Color.get(user=self.user, type='Body').code)

    def update_best_score(self):
        try:
            score = Score.select().where(Score.level == self.level.get()).order_by(Score.score.desc()).get()
            self.best_score.set(score.score)

        except:
            self.best_score.set(0)

    def check_head_and_body_collision(self):
        for body in self.snake.body:
            if check_collision(self.canvas, self.snake.head, body):
                messagebox.showinfo(meta.title, 'You loss')
                self.restart()
                break

    def check_eating_bait(self):
        if check_collision(self.canvas, self.snake.head, self.bait.item):
            self.bait.move()
            self.snake.grow()
            self.energy.set(self.energy.get() + self.bait.score)
            self.score.set(self.score.get() + 1)

    def check_energy(self):
        energy = self.energy.get()
        if energy > 0:
            if self.snake.direction != 'stop':
                self.energy.set(energy - 1)
        else:
            messagebox.showinfo(meta.title, 'Your energies finished!')
            self.restart()

    def set_level(self, level):
        self.level.set(level)
        self.energy.set(meta.base_energy)
        self.delay = .15 - (self.level.get() * 24) / 1000

        self.update_best_score()

    def reset_scores(self):
        submit = messagebox.askokcancel(meta.title, 'Are you sure you want to reset all your scores?')
        if submit:
            Score.delete().where(Score.user == self.user).execute()
            self.best_score.set(0)
            messagebox.showinfo(meta.title, 'Reset all your scores finished successfully!')

    def delete_account(self):
        submit = messagebox.askokcancel(meta.title, 'Are you sure you want to delete your account?')
        if submit:
            Score.delete().where(Score.user == self.user).execute()
            User.delete().where(User.username == self.user.username).execute()
            self.change_user(meta.default_user)
            self.destroy()
            messagebox.showinfo(meta.title, 'Your account deleted successfully!')

    def game_loop(self):
        while True:
            self.check_energy()
            self.check_eating_bait()
            self.check_head_and_body_collision()
            self.snake.move()
            self.bait.auto_move()
            self.update()
            time.sleep(self.delay)

    def init_menu(self):
        main_menu = tk.Menu(self.master)
        scores_menu = tk.Menu(main_menu, tearoff=False)
        account_menu = tk.Menu(main_menu, tearoff=False)
        manage_menu = tk.Menu(account_menu, tearoff=False)

        self.menus['main'] = main_menu
        self.menus['scores'] = scores_menu
        self.menus['account'] = account_menu
        self.menus['manage'] = manage_menu

        self.master.bind("<Control-i>", lambda event: dialogs.SigninDialog(self))
        self.master.bind("<Control-u>", lambda event: dialogs.SignupDialog(self))
        account_menu.add_command(label='Sign in', command=lambda: dialogs.SigninDialog(self), accelerator="Ctrl+I")
        account_menu.add_command(label='Sign up', command=lambda: dialogs.SignupDialog(self), accelerator="Ctrl+U")
        account_menu.add_separator()
        account_menu.add_cascade(label='Manage Account', menu=manage_menu)

        account_menu.entryconfig('Manage Account', state=tk.DISABLED)

        manage_menu.add_command(label='Change Username', command=lambda: dialogs.ChangeUsernameDialog(self))
        manage_menu.add_command(label='Change Password', command=lambda: dialogs.ChangePasswordDialog(self))
        manage_menu.add_command(label='Reset Scores', command=self.reset_scores)
        manage_menu.add_command(label='Delete Account', command=self.delete_account)

        scores_menu.add_command(label='Best Scores', command=lambda: dialogs.BestScoresDialog(self))
        scores_menu.add_command(label='My Scores', command=lambda: dialogs.MyScoresDialog(self))
        scores_menu.add_command(label='Records', command=lambda: dialogs.RecordsDialog(self))

        main_menu.add_cascade(label='Account Setting', menu=account_menu)
        main_menu.add_cascade(label='Scores', menu=scores_menu)
        main_menu.add_command(label='Setting', command=lambda: dialogs.SettingDialog(self))
        main_menu.add_command(label='About us', command=lambda: dialogs.AboutDialog(self.master))

        return main_menu
