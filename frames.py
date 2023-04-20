from abc import ABC, abstractmethod
from tkinter import messagebox, ttk
import tkinter as tk
import tksheet
import webbrowser

from database import User, Score, Config
import model
import meta


class GameFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.score = tk.IntVar()
        self.level = tk.IntVar()
        self.energy = tk.IntVar()
        self.best_score = tk.IntVar()
        self.username = tk.StringVar()

        labels_frame = tk.Frame(self)
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

        tk.Label(score_frame, text='Score:', font=meta.FONTS['medium']).pack(side=tk.LEFT, padx=5)
        tk.Label(score_frame, textvariable=self.score, font=meta.FONTS['medium']).pack(side=tk.RIGHT)

        tk.Label(bestscore_frame, text='Best Score:', font=meta.FONTS['medium']).pack(side=tk.LEFT, padx=5)
        tk.Label(bestscore_frame, textvariable=self.best_score, font=meta.FONTS['medium']).pack(side=tk.RIGHT)

        tk.Label(username_frame, text='User:', font=meta.FONTS['large']).pack(side=tk.TOP)
        tk.Label(username_frame, textvariable=self.username, font=meta.FONTS['large_italic'], width=13).pack(side=tk.BOTTOM)

        tk.Label(level_frame, text='Level:', font=meta.FONTS['medium']).pack(side=tk.LEFT, padx=5)
        tk.Label(level_frame, textvariable=self.level, font=meta.FONTS['medium']).pack(side=tk.RIGHT)

        tk.Label(energy_frame, text='Energy:', font=meta.FONTS['medium']).pack(side=tk.LEFT, padx=5)
        tk.Label(energy_frame, textvariable=self.energy, font=meta.FONTS['medium']).pack(side=tk.RIGHT)


        self.canvas = tk.Canvas(self, width=meta.FRAME_WIDTH, height=meta.FRAME_HEIGHT, highlightthickness=1.5, highlightbackground='black')
        self.canvas.pack(pady=5)


class SigninFrame(tk.Frame):
    def __init__(self, master, app=None, bind=False):
        super().__init__(master)
        self.app = app

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.pass_state = tk.StringVar()
        self.pass_state.set('*')

        ttk.Label(self, text='Username:').grid(row=1, column=1, pady=7, padx=5)
        self.combobox = ttk.Combobox(self, textvariable=self.username, width=17, values=list(map(lambda user: user.username, User.select())))
        self.combobox.grid(row=1, column=2, pady=7, padx=5)

        ttk.Label(self, text='Password:').grid(row=2, column=1, pady=7)
        pass_field = ttk.Entry(self, textvariable=self.password, show=self.pass_state.get())
        pass_field.grid(row=2, column=2, pady=7)

        ttk.Checkbutton(
            self, text='Show password', variable=self.pass_state, onvalue='', offvalue='*',
            command=lambda *args: pass_field.config(show=self.pass_state.get())
        ).grid(row=3, column=2, pady=5)

        self.button = ttk.Button(self, text='Sign in', width=10)
        self.button.grid(row=3, column=1, pady=5)

        if bind and self.app:
            self.button.config(command=self.signin)
            self.bind('<Return>', lambda _: self.signin())

    def signin(self, app=None):
        if app is None:
            app = self.app

        username = self.username.get()
        password = model.hash(self.password.get())

        user = User.get_or_none(username=username)
        if user:
            if app.user != user:
                if (password == user.password) or user.is_default:
                    app.restart()
                    app.change_user(user)
                    messagebox.showinfo(meta.TITLE, 'You logged in successfully!')
                    return True

                else:
                    messagebox.showwarning(meta.TITLE, 'Your password is incorrect!')
            else:
                messagebox.showinfo(meta.TITLE, 'Can not sign in into the current user!')
        else:
            messagebox.showwarning(meta.TITLE, 'Please enter a valid user!')

        return False


class SignupFrame(tk.Frame):
    def __init__(self, master, bind=False):
        super().__init__(master)

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.password.trace('w', lambda *args: self.check_match())
        self.confirm_password = tk.StringVar()
        self.confirm_password.trace('w', lambda *args: self.check_match())
        self.pass_state = tk.StringVar()
        self.pass_state.set('*')

        ttk.Label(self, text='Username:').grid(row=1, column=1, pady=7, padx=5)
        ttk.Entry(self, textvariable=self.username).grid(row=1, column=2, pady=7, padx=5)

        ttk.Label(self, text='Password:').grid(row=2, column=1, pady=7)
        ttk.Entry(self, show='*', textvariable=self.password).grid(row=2, column=2, pady=7)

        ttk.Label(self, text='Confirm Password:').grid(row=3, column=0, columnspan=2, pady=7)
        confirm_pass_field = ttk.Entry(self, textvariable=self.confirm_password, show=self.pass_state.get())
        confirm_pass_field.grid(row=3, column=2, pady=7)

        ttk.Checkbutton(
            self, text='Show password', variable=self.pass_state, onvalue='', offvalue='*',
            command=lambda *args: confirm_pass_field.config(show=self.pass_state.get())
        ).grid(row=4, column=0, columnspan=2, pady=5)

        self.button = ttk.Button(self, text='Sign up', width=10, state='disabled')
        self.button.grid(row=4, column=2, pady=5)

        if bind:
            self.button.config(command=self.signup)
            self.bind('<Return>', lambda _: self.signup())

    def check_match(self):
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        if (password == confirm_password) and password.strip():
            self.button.config(state=tk.NORMAL)
        else:
            self.button.config(state=tk.DISABLED)

    def signup(self):
        username = self.username.get()
        password = model.hash(self.password.get())

        if username:
            if not User.get_or_none(username=username):
                model.create_user(username=username, password=password)
                messagebox.showinfo(meta.TITLE, 'Your account created successfully! \nnow you most sign in')
                return True

            else:
                messagebox.showwarning(meta.TITLE, 'Username already exists!')
        else:
            messagebox.showwarning(meta.TITLE, 'Please enter a username')

        return False


class ChangePasswordFrame(tk.Frame):
    def __init__(self, master, app=None, bind=False):
        super().__init__(master)
        self.app = app

        self.old_password = tk.StringVar()
        self.new_password = tk.StringVar()
        self.new_password.trace('w', lambda *args: self.check_match())
        self.confirm_password = tk.StringVar()
        self.confirm_password.trace('w', lambda *args: self.check_match())
        self.password_state = tk.StringVar()
        self.password_state.set('*')

        ttk.Label(self, text='Old Password:').grid(row=1, column=2, pady=5)
        ttk.Entry(self, textvariable=self.old_password).grid(row=1, column=3, pady=5)

        ttk.Label(self, text='New Password:').grid(row=2, column=2, pady=5)
        ttk.Entry(self, show='*', textvariable=self.new_password).grid(row=2, column=3, pady=5)

        ttk.Label(self, text='Confirm Password:').grid(row=3, column=1, columnspan=2, pady=5)
        confirm_pass_field = ttk.Entry(self, textvariable=self.confirm_password, show=self.password_state.get())
        confirm_pass_field.grid(row=3, column=3, pady=5)

        ttk.Checkbutton(
            self, text='Show Password', variable=self.password_state, onvalue='', offvalue='*',
            command=lambda *args: confirm_pass_field.config(show=self.password_state.get())
        ).grid(row=4, column=1, columnspan=2, pady=3)

        self.button = ttk.Button(self, text='Change Password', state=tk.DISABLED, width=17)
        self.button.grid(row=4, column=3, pady=15)

        if bind and self.app:
            self.button.config(command=self.change_password)
            self.bind('<Return>', lambda _: self.change_password())

    def check_match(self):
        new_password = self.new_password.get()
        confirm_password = self.confirm_password.get()

        if (new_password == confirm_password) and new_password.strip():
            self.button.config(state=tk.NORMAL)
        else:
            self.button.config(state=tk.DISABLED)

    def change_password(self, app=None):
        if app is None:
            app = self.app

        old_password = self.old_password.get()
        new_password = self.new_password.get()
        confirm_password = self.confirm_password.get()

        if old_password.strip() and new_password.strip():
            if app.user.password == model.hash(old_password):
                if new_password == confirm_password:
                    new_password = model.hash(new_password)
                    User.update(password=new_password).where(User.username == app.user.username).execute()
                    messagebox.showinfo(meta.TITLE, 'Your password changed successfully!')
                    return True

                else:
                    messagebox.showwarning(meta.TITLE, 'Passwords not match!')
            else:
                messagebox.showwarning(meta.TITLE, 'Old password is incorrect!')
        else:
            messagebox.showwarning(meta.TITLE, 'Password field is empty!')

        return False


class ChangeUsernameFrame(tk.Frame):
    def __init__(self, master, app=None, bind=False):
        super().__init__(master)
        self.app = app

        self.username = tk.StringVar()

        ttk.Label(self, text='New Username:').grid(row=1, column=1, pady=10, padx=10)
        ttk.Entry(self, textvariable=self.username).grid(row=1, column=2, pady=5)

        self.button = ttk.Button(self, text='Change', width=12)
        self.button.grid(row=2, column=2, pady=5)

        if bind and self.app:
            self.button.config(command=self.change_username)
            self.bind('<Return>', lambda _: self.change_username())

    def change_username(self, app=None):
        if app is None:
            app = self.app

        new_username = self.username.get()
        old_username = app.user.username

        if new_username.strip():
            if new_username != old_username:
                if not User.get_or_none(username=new_username):
                    app.username = new_username
                    User.update(username=new_username).where(User.username == old_username).execute()
                    app.user.username = new_username
                    messagebox.showinfo(meta.TITLE, f'Your username changed from <{old_username}> to <{new_username}>')
                    return True

                else:
                    messagebox.showwarning(meta.TITLE, 'Username already exists!')
            else:
                messagebox.showwarning(meta.TITLE, "You can't change your username to the current username!")
        else:
            messagebox.showwarning(meta.TITLE, 'Username field is empty!')

        return False


class AboutUsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text='This game has made by Sina.F').grid(row=1, column=1, columnspan=2, pady=10)
        tk.Button(self, text='GitHub', width=8, command=lambda: webbrowser.open(meta.LINKS['github'])).grid(row=2, column=1, padx=7)
        tk.Button(self, text='Telegram', width=8, command=lambda: webbrowser.open(meta.LINKS['telegram'])).grid(row=2, column=2, padx=7)


class TableFrame(tk.Frame, ABC):
    def __init__(self, master):
        super().__init__(master)

        self.sheet = tksheet.Sheet(self, headers=self.header)
        self.sheet.hide(canvas='x_scrollbar')
        self.sheet.align('center')
        self.sheet.grid()
        self.sheet.enable_bindings()
        self.sheet.disable_bindings(meta.UNWANTED_BINDINGS)

    def load(self, *args, **kwargs):
        for row in self.fetch_data(*args, **kwargs):
            self.sheet.insert_row(row)

    @property
    @abstractmethod
    def header(self): pass

    @abstractmethod
    def fetch_data(self, *args, **kwargs): pass


class BestScoresTable(TableFrame):
    header = ['User', 'Score', 'Date']

    @classmethod
    def fetch_data(cls, level=2):
        rows = []
        scores = Score.select().where(Score.level == level).order_by(Score.score.desc())
        for counter, score in enumerate(scores, 1):
            rows.append([score.user.username, score.score, score.datetime.date()])

            if counter >= meta.BEST_SCORES_LIMIT:
                break

        return rows


class MyScoresTable(TableFrame):
    header = ['Score', 'Date', 'Time']

    @classmethod
    def fetch_data(cls, user=meta.default_user):
        rows = []
        for score in Score.select().where(Score.level == Config.fetch(user=user, label='Level'),
                                          Score.user == user).order_by(Score.score.desc()):
            rows.append([score.score, score.datetime.date(), score.datetime.time().strftime('%H:%M:%S')])

        return rows


class RecordsTable(TableFrame):
    header = ['Level', 'Your Record', 'Record']

    @classmethod
    def fetch_data(cls, user=meta.default_user):
        rows = []
        for level in range(1, 4):
            try:
                global_record = Score.select().where(Score.level == level).order_by(Score.score.desc()).get()
            except Exception:
                global_record = None

            try:
                user_record = Score.select().where(Score.level == level, Score.user == user).order_by(Score.score.desc()).get()
            except Exception:
                user_record = None

            rows.append([
                level,
                user_record.score if user_record else '-',
                f'{global_record.score} ({global_record.user.username})' if global_record else '-'
            ])

        return rows
