import tkinter as tk
import os

import meta
import model


def get_geometry(root):
    """ This function return a geometry to put app on center-center """

    scr_width = int(root.winfo_screenwidth())
    scr_height = int(root.winfo_screenheight())
    start_width = int((scr_width / 2) - 250)
    start_height = int((scr_height / 2) - 330)

    return f"{meta.WIDTH}x{meta.HEIGHT}+{start_width}+{start_height}"



if __name__ == "__main__":
    root = tk.Tk()
    root.title(meta.TITLE)
    root.geometry(get_geometry(root))
    root.resizable(False, False)
    if os.path.exists(meta.ICON_PATH):
        root.iconbitmap(default=meta.ICON_PATH)

    app = model.App(root)
    root.mainloop()
