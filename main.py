import tkinter as tk
import os

import meta
import model


if __name__ == "__main__":
    root = tk.Tk()
    root.title(meta.title)
    root.geometry(model.get_geometry(root))
    root.resizable(False, False)
    if os.path.exists(meta.icon_path):
        root.iconbitmap(default=meta.icon_path)

    app = model.App(root)
    app.mainloop()
