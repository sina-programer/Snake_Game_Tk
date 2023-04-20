from tkinter import simpledialog, colorchooser, messagebox
import tkinter as tk
import tksheet

from database import User, Score, Config
import frames
import meta


def beep():
    if meta.IS_WINDOWS:
        import winsound
        winsound.MessageBeep()



class BaseDialog(simpledialog.Dialog):
    def __init__(self, app, title):
        self.app = app
        self.app.pause()

        super().__init__(self.app.master, title)

    def destroy(self):
        self.forget(self)
        self.app.pause()

    def buttonbox(self):
        pass


class ChangePasswordDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, 'Change Password')

    def body(self, frame):
        self.frame = frames.ChangePasswordFrame(frame)
        self.frame.pack(pady=10, padx=10)
        self.frame.button.config(command=self.change_password)
        self.bind('<Return>', lambda _: self.change_password())
        self.resizable(False, False)
        beep()

    def change_password(self):
        if self.frame.change_password(app=self.app):
            self.destroy()


class ChangeUsernameDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, 'Change Username')

    def body(self, frame):
        self.frame = frames.ChangeUsernameFrame(frame)
        self.frame.pack(pady=10, padx=10)
        self.frame.button.config(command=self.change_username)
        self.bind('<Return>', lambda _: self.change_username())
        self.resizable(False, False)
        beep()

    def change_username(self):
        if self.frame.change_username(self.app):
            self.destroy()


class SignupDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, 'Sign up')

    def body(self, frame):
        self.config(menu=self.init_menu())

        self.frame = frames.SignupFrame(frame)
        self.frame.pack(pady=10, padx=10)
        self.frame.button.config(command=self.signup)
        self.bind('<Return>', lambda _: self.signup())
        self.resizable(False, False)
        beep()

    def signup(self):
        if self.frame.signup():
            self.destroy()

    def signin(self):
        self.destroy()
        SigninDialog(self.app)

    def init_menu(self):
        menu = tk.Menu(self)
        menu.add_command(label='Sign in', command=self.signin)

        return menu


class SigninDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, 'Sign in')

    def body(self, frame):
        self.config(menu=self.init_menu())

        self.frame = frames.SigninFrame(frame)
        self.frame.pack(pady=10, padx=10)
        self.frame.button.config(command=self.signin)
        self.bind('<Return>', lambda _: self.signin())
        self.resizable(False, False)
        beep()

    def signin(self):
        if self.frame.signin(self.app):
            self.destroy()

    def signup(self):
        self.destroy()
        SignupDialog(self.app)

    def init_menu(self):
        menu = tk.Menu(self)
        menu.add_command(label='Sign up', command=self.signup)

        return menu


class BestScoresDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, f'Best Scores (level={app.level})')

    def body(self, frame):
        self.table = frames.BestScoresTable(frame)
        self.table.load(level=self.app.level)
        self.table.pack()
        self.resizable(False, False)
        beep()


class MyScoresDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, f'My Scores ({app.username} | level={app.level})')

    def body(self, frame):
        self.table = frames.MyScoresTable(frame)
        self.table.load(user=self.app.user)
        self.table.pack()
        self.resizable(False, False)
        beep()


class RecordsDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, f'Records')

    def body(self, frame):
        self.table = frames.RecordsTable(frame)
        self.table.load(user=self.app.user)
        self.table.pack()
        self.resizable(False, False)
        beep()


class SettingDialog(BaseDialog):
    def __init__(self, app):
        self.bg_color_btn = None
        self.head_color_btn = None
        self.body_color_btn = None
        if app.user.is_default:
            self.state = tk.DISABLED
        else:
            self.state = tk.NORMAL

        self.level_var = tk.IntVar()

        super().__init__(app, 'Setting')

    def body(self, frame):
        self.level_var.set(self.app.level)

        tk.Label(frame, text='Level:').grid(row=1, column=1)
        tk.Scale(frame, from_=1, to=3, variable=self.level_var, orient=tk.HORIZONTAL).grid(row=1, column=2, columnspan=3, pady=12)

        tk.Label(frame, text='Snake Head Color:', state=self.state).grid(row=2, column=1, columnspan=3, pady=5)
        self.head_color_btn = tk.Button(frame, width=2, command=self.set_head_color, state=self.state,
                                        bg=Config.fetch(user=self.app.user, label='Head'))
        self.head_color_btn.grid(row=2, column=4, pady=5)

        tk.Label(frame, text='Snake Body Color:', state=self.state).grid(row=3, column=1, columnspan=3, pady=5)
        self.body_color_btn = tk.Button(frame, width=2, command=self.set_body_color, state=self.state,
                                        bg=Config.fetch(user=self.app.user, label='Body'))
        self.body_color_btn.grid(row=3, column=4, pady=5)

        tk.Label(frame, text='Background Color:', state=self.state).grid(row=4, column=1, columnspan=3, pady=5)
        self.bg_color_btn = tk.Button(frame, width=2, command=self.set_bg_color, state=self.state,
                                      bg=Config.fetch(user=self.app.user, label='Background'))
        self.bg_color_btn.grid(row=4, column=4, pady=5)

        tk.Button(frame, text='Reset', width=10, command=self.reset).grid(row=5, column=1, columnspan=2, pady=20, padx=5)
        tk.Button(frame, text='Apply', width=10, command=self.apply).grid(row=5, column=3, columnspan=2, pady=20, padx=5)


        self.bind('<Return>', lambda _: self.apply())
        self.bind('<Escape>', lambda _: self.reset())

        self.geometry('200x240')
        self.resizable(False, False)
        beep()

        return frame

    def apply(self):
        if self.level_var.get() != self.app.level and messagebox.askokcancel(
                meta.TITLE, 'Are you sure you want to restart the game? (score will save)'):
            self.app.restart()
            self.app.set_level(self.level_var.get())

        Config.update(value=self.head_color_btn['bg']).where(Config.user == self.app.user, Config.label == 'Head').execute()
        Config.update(value=self.body_color_btn['bg']).where(Config.user == self.app.user, Config.label == 'Body').execute()
        Config.update(value=self.bg_color_btn['bg']).where(Config.user == self.app.user, Config.label == 'Background').execute()

        self.app.update_personalizations()

    def set_head_color(self):
        new_head_color = colorchooser.askcolor(initialcolor=self.head_color_btn['bg'])[1]
        self.head_color_btn.config(bg=new_head_color)

    def set_body_color(self):
        new_body_color = colorchooser.askcolor(initialcolor=self.body_color_btn['bg'])[1]
        self.body_color_btn.config(bg=new_body_color)

    def set_bg_color(self):
        new_bg_color = colorchooser.askcolor(initialcolor=self.bg_color_btn['bg'])[1]
        self.bg_color_btn.config(bg=new_bg_color)

    def reset(self):
        self.head_color_btn.config(bg=Config.fetch(user=self.app.user, label='Head'))
        self.body_color_btn.config(bg=Config.fetch(user=self.app.user, label='Body'))
        self.bg_color_btn.config(bg=Config.fetch(user=self.app.user, label='Background'))
        self.level_var.set(self.app.level)


class AboutDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app.master, 'About us')

    def body(self, frame):
        self.frame = frames.AboutUsFrame(frame)
        self.frame.pack(pady=10, padx=10)
        self.resizable(False, False)
        beep()
