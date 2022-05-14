from tkinter import simpledialog, colorchooser, messagebox
import tkinter as tk
import webbrowser
import hashlib
import tksheet

from database import User, Score, Color
import meta

if meta.is_windows:
    import winsound


class BaseDialog(simpledialog.Dialog):
    def __init__(self, parent, title, app=None):
        self.parent = parent
        if app:
            self.app = app

        super().__init__(self.parent, title)

    def buttonbox(self):
        pass


class ChangePasswordDialog(BaseDialog):
    def __init__(self, app):
        self.old_pass_var = tk.StringVar()
        self.new_pass_var = tk.StringVar()
        self.confirm_pass_var = tk.StringVar()

        self.show_pass_state = tk.StringVar()
        self.show_pass_state.set('*')
        super().__init__(app.master, 'Change Password', app)

    def body(self, frame):
        tk.Label(frame, text='Old password:').grid(row=1, column=2, pady=5)
        tk.Entry(frame, textvariable=self.old_pass_var).grid(row=1, column=3, pady=5)

        tk.Label(frame, text='New password:').grid(row=2, column=2, pady=5)
        tk.Entry(frame, show='*', textvariable=self.new_pass_var).grid(row=2, column=3, pady=5)

        tk.Label(frame, text='Confirm password:').grid(row=3, column=1, columnspan=2, pady=5)
        confirm_pass_field = tk.Entry(frame, textvariable=self.confirm_pass_var, show=self.show_pass_state.get())
        confirm_pass_field.grid(row=3, column=3, pady=5)

        tk.Checkbutton(frame, text='Show password', variabl=self.show_pass_state, onvalue='', offvalue='*',
                       command=lambda *args: confirm_pass_field.config(show=self.show_pass_state.get())
                       ).grid(row=4, column=1, columnspan=2, pady=3)

        tk.Button(frame, text='Change Password', width=15, command=self.change_password).grid(row=4, column=3, pady=15)

        self.bind('<Return>', lambda _: self.change_password())

        self.geometry('270x160')
        self.resizable(False, False)
        if meta.is_windows:
            winsound.MessageBeep()

        return frame

    def change_password(self):
        old_password = self.old_pass_var.get()
        new_password = self.new_pass_var.get()
        confirm_password = self.confirm_pass_var.get()

        if old_password.strip() and new_password.strip():
            if self.app.user.password == hashlib.sha256(old_password.encode()).hexdigest():
                if new_password == confirm_password:
                    new_password = hashlib.sha256(new_password.encode()).hexdigest()
                    User.update(password=new_password).where(User.username == self.app.user.username).execute()
                    messagebox.showinfo(meta.title, 'Your password changed successfully!')

                else:
                    messagebox.showwarning(meta.title, 'Passwords not match!')
            else:
                messagebox.showwarning(meta.title, 'Your password is incorrect!')
        else:
            messagebox.showwarning(meta.title, 'Password field is empty!')


class ChangeUsernameDialog(BaseDialog):
    def __init__(self, app):
        self.user_var = tk.StringVar()
        super().__init__(app.master, 'Change Username', app)

    def body(self, frame):
        tk.Label(frame, text='New Username:').grid(row=1, column=1, pady=10, padx=10)
        tk.Entry(frame, textvariable=self.user_var).grid(row=1, column=2, pady=5)
        tk.Button(frame, text='Change', width=12, command=self.change_username).grid(row=2, column=2, pady=5)

        self.bind('<Return>', lambda _: self.change_username())

        self.geometry('270x90')
        self.resizable(False, False)
        if meta.is_windows:
            winsound.MessageBeep()

        return frame

    def change_username(self):
        new_username = self.user_var.get()
        old_username = self.app.user.username

        if new_username.strip():
            if new_username != old_username:
                if not User.get_or_none(username=new_username):
                    self.app.username_lbl.config(text=new_username)
                    User.update(username=new_username).where(User.username == self.app.user.username).execute()
                    messagebox.showinfo(meta.title, f'Your username changed from <{old_username}> to <{new_username}>')

                else:
                    messagebox.showwarning(meta.title, 'Username already exists!')
            else:
                messagebox.showwarning(meta.title, "You can't change your username to the current username!")
        else:
            messagebox.showwarning(meta.title, 'Username field is empty!')


class SignupDialog(BaseDialog):
    def __init__(self, app):
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        self.pass_var.trace('w', lambda *args: self.check_match())
        self.confirm_pass_var = tk.StringVar()
        self.confirm_pass_var.trace('w', lambda *args: self.check_match())

        self.signup_btn = None
        self.state_label = None

        self.show_pass_state = tk.StringVar()
        self.show_pass_state.set('*')
        super().__init__(app.master, 'Sign up', app)

    def body(self, frame):
        tk.Label(frame, text='Username:').grid(row=0, column=1, pady=5)
        tk.Entry(frame, textvariable=self.user_var).grid(row=0, column=2, pady=5)

        tk.Label(frame, text='Password:').grid(row=1, column=1, pady=5)
        tk.Entry(frame, show='*', textvariable=self.pass_var).grid(row=1, column=2, pady=5)

        tk.Label(frame, text='Confirm password:').grid(row=2, column=0, columnspan=2, pady=5)
        confirm_pass_field = tk.Entry(frame, show=self.show_pass_state.get(), textvariable=self.confirm_pass_var)
        confirm_pass_field.grid(row=2, column=2, pady=5)

        tk.Checkbutton(frame, text='Show password', variabl=self.show_pass_state, onvalue='', offvalue='*',
                       command=lambda *args: confirm_pass_field.config(show=self.show_pass_state.get())
                       ).grid(row=3, column=0, columnspan=2, pady=3)

        self.state_label = tk.Label(frame)
        self.state_label.grid(row=3, column=2, pady=3)

        self.signup_btn = tk.Button(frame, text='Sign up', width=10, state='disabled', command=self.signup)
        self.signup_btn.grid(row=4, column=2, pady=5)
        tk.Button(frame, text='Sign in', width=10, command=self.signin).grid(row=4, column=0, columnspan=2, pady=5)

        self.bind('<Return>', lambda _: self.signup())

        self.geometry('270x180')
        self.resizable(False, False)
        if meta.is_windows:
            winsound.MessageBeep()

        return frame

    def signup(self):
        username = self.user_var.get()
        password = self.pass_var.get()
        password = hashlib.sha256(password.encode()).hexdigest()

        if not User.get_or_none(username=username):
            user = User.create(username=username, password=password)
            for ctype, color in meta.default_colors.items():
                Color.create(user=user, code=color, type=ctype)

            messagebox.showinfo(meta.title, 'Your account created successfully! \nnow you most sign in')

        else:
            messagebox.showwarning(meta.title, 'Username already exists!')

    def check_match(self):
        password = self.pass_var.get()
        confirm_password = self.confirm_pass_var.get()

        if not password or not confirm_password:
            self.state_label.config(text='')
            self.signup_btn.config(state='disabled')

        elif password != confirm_password:
            self.state_label.config(text='not match!', fg='red')
            self.signup_btn.config(state='disabled')

        else:
            self.state_label.config(text='match!', fg='green')
            self.signup_btn.config(state='normal')

    def signin(self):
        self.destroy()
        SigninDialog(self.app)


class SigninDialog(BaseDialog):
    def __init__(self, app):
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()

        self.show_pass_state = tk.StringVar()
        self.show_pass_state.set('*')
        super().__init__(app.master, 'Sign in', app)

    def body(self, frame):
        tk.Label(frame, text='Username:').grid(row=1, column=1, pady=5)
        tk.Entry(frame, textvariable=self.user_var).grid(row=1, column=2, pady=5)

        tk.Label(frame, text='Password:').grid(row=2, column=1, pady=5)
        pass_field = tk.Entry(frame, textvariable=self.pass_var, show=self.show_pass_state.get())
        pass_field.grid(row=2, column=2, pady=5)

        tk.Checkbutton(frame, text='Show password', variabl=self.show_pass_state, onvalue='', offvalue='*',
                       command=lambda *args: pass_field.config(show=self.show_pass_state.get())
                       ).grid(row=3, column=2, pady=5)

        tk.Button(frame, text='Sign up', width=10, command=self.signup).grid(row=4, column=1, pady=5)
        tk.Button(frame, text='Sign in', width=10, command=self.signin).grid(row=4, column=2, pady=5)

        self.bind('<Return>', lambda _: self.signin())

        self.geometry('250x150')
        self.resizable(False, False)
        if meta.is_windows:
            winsound.MessageBeep()

        return frame

    def signin(self):
        username = self.user_var.get()
        password = self.pass_var.get()
        password = hashlib.sha256(password.encode()).hexdigest()

        user = User.get_or_none(username=username)
        if user:
            if password == user.password or username == meta.default_username:
                self.app.restart()
                self.app.change_user(user)
                messagebox.showinfo(meta.title, 'You logged in successfully!')

            else:
                messagebox.showwarning(meta.title, 'Your password is incorrect!')
        else:
            messagebox.showwarning(meta.title, 'Please enter a valid user!')

    def signup(self):
        self.destroy()
        SignupDialog(self.app)


class BestScoresDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app.master, 'Best Scores', app)

    def body(self, frame):
        sheet = tksheet.Sheet(self, headers=['User', 'Score', 'Date'])
        sheet.pack(pady=5)
        sheet.align('center')
        sheet.hide(canvas='x_scrollbar')

        for counter, score in enumerate(Score.select().where(Score.level == self.app.level.get()).order_by(Score.score.desc()), 1):
            sheet.insert_row([score.user.username, score.score, score.datetime.date()])

            if counter >= meta.best_scores_limit:
                break

        sheet.enable_bindings()
        sheet.disable_bindings(meta.unwanted_bindings)

        self.resizable(False, False)
        self.geometry('440x260')
        if meta.is_windows:
            winsound.MessageBeep()

        return frame


class MyScoresDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app.master, f'My Scores ({app.user.username})', app)

    def body(self, frame):
        sheet = tksheet.Sheet(self, headers=['Score', 'Date', 'Time'])
        sheet.pack(pady=5)
        sheet.align('center')
        sheet.hide(canvas='x_scrollbar')

        for score in Score.select().where(Score.level == self.app.level.get(),
                                          Score.user == self.app.user).order_by(Score.score.desc()):

            sheet.insert_row([score.score, score.datetime.date(), score.datetime.time().strftime('%H:%M:%S')])

        sheet.enable_bindings()
        sheet.disable_bindings(meta.unwanted_bindings)

        self.resizable(False, False)
        self.geometry('440x260')
        if meta.is_windows:
            winsound.MessageBeep()

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
                record.score if record else '-'
            ])

        sheet.enable_bindings()
        sheet.disable_bindings(meta.unwanted_bindings)

        self.resizable(False, False)
        self.geometry('400x100')
        if meta.is_windows:
            winsound.MessageBeep()

        return frame


class SettingDialog(BaseDialog):
    def __init__(self, app):
        self.bg_color_btn = None
        self.head_color_btn = None
        self.body_color_btn = None
        self.state = tk.DISABLED if app.user == meta.default_user else tk.NORMAL

        self.level_var = tk.IntVar()

        super().__init__(app.master, 'Setting', app)

    def body(self, frame):
        self.level_var.set(self.app.level.get())

        tk.Label(frame, text='Level:').grid(row=1, column=1)
        tk.Scale(frame, from_=1, to=3, variable=self.level_var, orient=tk.HORIZONTAL).grid(row=1, column=2, columnspan=3, pady=12)

        tk.Label(frame, text='Snake Head Color:').grid(row=2, column=1, columnspan=3, pady=5)
        self.head_color_btn = tk.Button(frame, width=2, command=self.set_head_color, state=self.state,
                                        bg=Color.get(user=self.app.user, type='Head').code)
        self.head_color_btn.grid(row=2, column=4, pady=5)

        tk.Label(frame, text='Snake Body Color:').grid(row=3, column=1, columnspan=3, pady=5)
        self.body_color_btn = tk.Button(frame, width=2, command=self.set_body_color, state=self.state,
                                        bg=Color.get(user=self.app.user, type='Body').code)
        self.body_color_btn.grid(row=3, column=4, pady=5)

        tk.Label(frame, text='Background Color:').grid(row=4, column=1, columnspan=3, pady=5)
        self.bg_color_btn = tk.Button(frame, width=2, command=self.set_bg_color, state=self.state,
                                      bg=Color.get(user=self.app.user, type='Background').code)
        self.bg_color_btn.grid(row=4, column=4, pady=5)

        tk.Button(frame, text='Reset', width=10, command=self.reset).grid(row=5, column=1, columnspan=2, pady=20, padx=5)
        tk.Button(frame, text='Apply', width=10, command=self.apply).grid(row=5, column=3, columnspan=2, pady=20, padx=5)


        self.bind('<Return>', lambda _: self.apply())
        self.bind('<Escape>', lambda _: self.reset())

        self.geometry('200x240')
        self.resizable(False, False)
        if meta.is_windows:
            winsound.MessageBeep()

        return frame

    def apply(self):
        if self.level_var.get() != self.app.level.get() and messagebox.askokcancel(
                meta.title, 'Are you sure you want to restart the game? (score will save)'):
            self.app.restart()
            self.app.set_level(self.level_var.get())

        Color.update(code=self.head_color_btn['bg']).where(Color.user == self.app.user, Color.type == 'Head').execute()
        Color.update(code=self.body_color_btn['bg']).where(Color.user == self.app.user, Color.type == 'Body').execute()
        Color.update(code=self.bg_color_btn['bg']).where(Color.user == self.app.user, Color.type == 'Background').execute()

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
        self.head_color_btn.config(bg=Color.get(user=self.app.user, type='Head').code)
        self.body_color_btn.config(bg=Color.get(user=self.app.user, type='Body').code)
        self.bg_color_btn.config(bg=Color.get(user=self.app.user, type='Background').code)
        self.level_var.set(self.app.level.get())


class AboutDialog(BaseDialog):
    def __init__(self, parent):
        if meta.is_windows:
            winsound.MessageBeep()
        super().__init__(parent, 'About us')

    def body(self, frame):
        tk.Label(frame, text='This game made by Sina.f').grid(row=1, column=1, columnspan=2, pady=15)

        tk.Button(frame, text='GitHub', width=8, command=lambda: webbrowser.open(meta.links['github'])
                  ).grid(row=2, column=1, padx=7)
        tk.Button(frame, text='Telegram', width=8, command=lambda: webbrowser.open(meta.links['telegram'])
                  ).grid(row=2, column=2, padx=7)

        self.geometry('220x100')
        self.resizable(False, False)

        return frame
