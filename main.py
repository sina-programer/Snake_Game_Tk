from tkinter import messagebox
import tkinter as tk
import datetime as dt
import os

from objects import Bait, Snake
from database import User, Score, Config

import meta
import model
import frames
import dialogs


class App:
    def __init__(self):
        self.master = App.create_master()

        self.menus = {}
        self.delay = None
        self._pause = True

        self.login_frame = frames.LoginFrame(self.master)
        self.game_frame = frames.GameFrame(self.master)
        self.login_frame.grid(row=0, column=0)
        self.game_frame.grid(row=0, column=0)
        self.login_frame.tkraise()
        self.login_frame.signin_frame.button.config(command=self.signin)

        self.user = meta.default_user
        self.snake = Snake(self.game_frame.canvas)
        self.bait = Bait(self.game_frame.canvas, energy=30, timeout=60, color='green')

        self.master.config(menu=self.init_menu())
        self.master.bind('<Up>', lambda _: self.snake.set_direction('up'))
        self.master.bind('<Down>', lambda _: self.snake.set_direction('down'))
        self.master.bind('<Left>', lambda _: self.snake.set_direction('left'))
        self.master.bind('<Right>', lambda _: self.snake.set_direction('right'))
        self.master.bind('<Escape>', lambda _: self.pause())

        self.menus['main'].entryconfig('Account Setting', state=tk.DISABLED)
        self.menus['main'].entryconfig('Scores', state=tk.DISABLED)
        self.menus['main'].entryconfig('Setting', state=tk.DISABLED)
        self.menus['main'].entryconfig('About us', state=tk.DISABLED)

        self.guide_text_id = self.game_frame.canvas.create_text(meta.CANVAS_WIDTH//2, meta.CANVAS_HEIGHT//2 - (meta.UNIT_SIZE*2), text='Press <enter> to start the game', font=meta.FONTS['medium'])
        self.change_user(self.user)
        self.master.mainloop()

    @property
    def score(self):
        return self.game_frame.score.get()

    @score.setter
    def score(self, value):
        self.game_frame.score.set(value)

    @property
    def level(self):
        return self.game_frame.level.get()

    @level.setter
    def level(self, value):
        self.game_frame.level.set(value)

    @property
    def energy(self):
        return self.game_frame.energy.get()

    @energy.setter
    def energy(self, value):
        self.game_frame.energy.set(value)

    @property
    def best_score(self):
        return self.game_frame.best_score.get()

    @best_score.setter
    def best_score(self, value):
        self.game_frame.best_score.set(value)

    @property
    def username(self):
        return self.game_frame.username.get()

    @username.setter
    def username(self, value):
        self.game_frame.username.set(value)

    @classmethod
    def create_master(cls):
        root = tk.Tk()
        root.title(meta.TITLE)
        root.geometry(get_geometry(root))
        root.resizable(False, False)
        if os.path.exists(meta.ICON_PATH):
            root.iconbitmap(default=meta.ICON_PATH)

        return root

    def signin(self):
        if self.login_frame.signin_frame.signin(app=self):
            self.master.bind('<Return>', lambda _: self.start())
            self.master.bind("<Control-i>", lambda event: dialogs.SigninDialog(self))
            self.master.bind("<Control-u>", lambda event: dialogs.SignupDialog(self))

            self.login_frame.destroy()

            self.menus['main'].entryconfig('Account Setting', state=tk.NORMAL)
            self.menus['main'].entryconfig('Scores', state=tk.NORMAL)
            self.menus['main'].entryconfig('Setting', state=tk.NORMAL)
            self.menus['main'].entryconfig('About us', state=tk.NORMAL)

    def restart(self):
        if self.score:  # auto save score when changing level meanwhile playing
            Score.create(user=self.user, score=self.score, level=self.level, datetime=dt.datetime.now())

        if self.score > self.best_score:
            self.best_score = self.score

        self.energy = meta.BASE_ENERGY
        self.score = 0
        self.snake.reset()
        self.bait.reset()
        self._pause = True

    def change_user(self, user):
        self.user = user
        self.username = self.user.username
        self.update_personalizations()
        self.set_level(Config.fetch(user=user, label='Level'))

        if self.user.is_default:
            self.menus['account'].entryconfig('Manage Account', state=tk.DISABLED)
        else:
            self.menus['account'].entryconfig('Manage Account', state=tk.NORMAL)

    def update_personalizations(self):
        self.game_frame.canvas.config(bg=Config.fetch(user=self.user, label='Background'))
        self.snake.change_head_color(Config.fetch(user=self.user, label='Head'))
        self.snake.change_body_color(Config.fetch(user=self.user, label='Body'))

    def update_best_score(self):
        try:
            best_score = Score.select().where(Score.level == self.level, Score.user == self.user).order_by(Score.score.desc()).get()
            self.best_score = best_score.score

        except:
            self.best_score = 0

    def check_head_and_body_collision(self):
        for body in self.snake.body:
            if model.check_collision(self.game_frame.canvas, self.snake.head, body):
                messagebox.showinfo(meta.TITLE, 'You lost')
                self.restart()
                break

    def check_eating_bait(self):
        if model.check_collision(self.game_frame.canvas, self.snake.head, self.bait.item):
            self.bait.move()
            self.snake.grow()
            self.energy += self.bait.energy
            self.score += 1

    def check_energy(self):
        if self.energy > 0:
            if not self._pause:
                self.energy -= 1
        else:
            messagebox.showinfo(meta.TITLE, 'Your energies finished!')
            self.restart()

    def set_level(self, level):
        self.level = level
        self.energy = meta.BASE_ENERGY
        self.delay = (150 - (self.level * 24))

        Config.update(value=level).where(Config.user == self.user, Config.label == 'Level').execute()
        self.update_best_score()

    def reset_scores(self):
        if messagebox.askokcancel(meta.TITLE, 'Are you sure you want to reset all your scores?'):
            Score.delete().where(Score.user == self.user).execute()
            self.best_score = 0
            messagebox.showinfo(meta.TITLE, 'All your scores were reset!')

    def delete_account(self):
        if messagebox.askokcancel(meta.TITLE, 'Are you sure you want to delete your account?'):
            Score.delete().where(Score.user == self.user).execute()
            User.delete().where(User.username == self.user.username).execute()
            self.change_user(meta.default_user)
            messagebox.showinfo(meta.TITLE, 'Your account has deleted successfully!')

    def start(self):
        self.game_frame.canvas.delete(self.guide_text_id)
        self.master.unbind('<Return>')
        self.snake.set_direction('up')
        self._pause = False
        self.game_loop()

    def game_loop(self):
        if not self._pause:
            self.check_eating_bait()
            self.check_energy()
            self.check_head_and_body_collision()
            self.snake.move()
            self.bait.auto_move()
            self.game_frame.update()

        self.master.after(self.delay, self.game_loop)

    def pause(self):
        self._pause = not self._pause

    def init_menu(self):
        main_menu = tk.Menu(self.master)
        scores_menu = tk.Menu(main_menu, tearoff=False)
        account_menu = tk.Menu(main_menu, tearoff=False)
        manage_menu = tk.Menu(account_menu, tearoff=False)

        self.menus['main'] = main_menu
        self.menus['scores'] = scores_menu
        self.menus['account'] = account_menu
        self.menus['manage'] = manage_menu

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
        main_menu.add_command(label='About us', command=lambda: dialogs.AboutDialog(self))

        return main_menu



def get_geometry(root):
    """ This function return a geometry to put app on center-center """

    scr_width = int(root.winfo_screenwidth())
    scr_height = int(root.winfo_screenheight())
    start_width = int((scr_width / 2) - 250)
    start_height = int((scr_height / 2) - 330)

    return f"{meta.WIDTH}x{meta.HEIGHT}+{start_width}+{start_height}"



if __name__ == "__main__":
    app = App()
