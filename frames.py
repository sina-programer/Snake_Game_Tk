from tkinter import messagebox
from tkinter import ttk
import tkinter as tk

from database import User
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
    def __init__(self, master, app=None):
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

        if self.app:
            self.button.config(command=lambda: self.signin(self.app))

    def signin(self, app=None):
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
    def __init__(self, master):
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

        ttk.Label(self, text='Confirm Password:').grid(row=3, column=1, pady=7)
        confirm_pass_field = ttk.Entry(self, textvariable=self.confirm_password, show=self.pass_state.get())
        confirm_pass_field.grid(row=3, column=2, pady=7)

        ttk.Checkbutton(
            self, text='Show password', variable=self.pass_state, onvalue='', offvalue='*',
            command=lambda *args: confirm_pass_field.config(show=self.pass_state.get())
        ).grid(row=4, column=2, pady=5)

        self.button = ttk.Button(self, text='Sign up', width=10, state='disabled')
        self.button.grid(row=4, column=1, pady=5)

    def check_match(self):
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        if (password == confirm_password) and password:
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
