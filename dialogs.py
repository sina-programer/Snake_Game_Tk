from tkinter import simpledialog, colorchooser, messagebox
import tkinter as tk
import webbrowser
import tksheet

from database import User, Score, Config
import frames
import model
import meta


def beep():
    if meta.IS_WINDOWS:
        import winsound
        winsound.MessageBeep()



class BaseDialog(simpledialog.Dialog):
    def __init__(self, parent, title, app=None):
        self.parent = parent
        self.app = app

        super().__init__(self.parent, title)

    def buttonbox(self):
        pass


class ChangePasswordDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app.master, 'Change Password', app)

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
        super().__init__(app.master, 'Change Username', app)

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
        super().__init__(app.master, 'Sign up', app)

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
        super().__init__(app.master, 'Sign in', app)

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
        super().__init__(app.master, 'Best Scores', app)

    def body(self, frame):
        sheet = tksheet.Sheet(self, headers=['User', 'Score', 'Date'])
        sheet.pack(pady=5)
        sheet.align('center')
        sheet.hide(canvas='x_scrollbar')

        scores = Score.select().where(Score.level == self.app.level).order_by(Score.score.desc())
        for counter, score in enumerate(scores, 1):
            sheet.insert_row([score.user.username, score.score, score.datetime.date()])

            if counter >= meta.BEST_SCORES_LIMIT:
                break

        sheet.enable_bindings()
        sheet.disable_bindings(meta.UNWANTED_BINDINGS)

        self.resizable(False, False)
        self.geometry('440x260')
        beep()

        return frame


class MyScoresDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app.master, f'My Scores ({app.user.username})', app)

    def body(self, frame):
        sheet = tksheet.Sheet(self, headers=['Score', 'Date', 'Time'])
        sheet.pack(pady=5)
        sheet.align('center')
        sheet.hide(canvas='x_scrollbar')

        for score in Score.select().where(Score.level == self.app.level,
                                          Score.user == self.app.user).order_by(Score.score.desc()):

            sheet.insert_row([score.score, score.datetime.date(), score.datetime.time().strftime('%H:%M:%S')])

        sheet.enable_bindings()
        sheet.disable_bindings(meta.UNWANTED_BINDINGS)

        self.resizable(False, False)
        self.geometry('440x260')
        beep()

        return frame


class RecordsDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app.master, f'Records', app)

    def body(self, frame):
        sheet = tksheet.Sheet(frame, headers=['Level', 'Your record', 'Record'])
        sheet.grid()
        sheet.align('center')
        sheet.hide(canvas='x_scrollbar')

        for level in range(1, 4):
            try:
                record = Score.select().where(Score.level == level).order_by(Score.score.desc()).get()
            except Exception:
                record = None

            try:
                score = Score.select().where(Score.level == level,
                                             Score.user == self.app.user).order_by(Score.score.desc()).get()
            except Exception:
                score = None

            sheet.insert_row([
                level,
                score.score if score else '-',
                f'{record.score} ({record.user.username})' if record else '-'
            ])

        sheet.enable_bindings()
        sheet.disable_bindings(meta.UNWANTED_BINDINGS)

        self.resizable(False, False)
        self.geometry('400x100')
        beep()

        return frame


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

        super().__init__(app.master, 'Setting', app)

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
    def __init__(self, parent):
        super().__init__(parent, 'About us')

    def body(self, frame):
        self.frame = frames.AboutUsFrame(frame)
        self.frame.pack(pady=10, padx=10)
        self.resizable(False, False)
        beep()
