import tkinter as tk

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
