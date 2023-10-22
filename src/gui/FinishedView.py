import tkinter as tk
from typing import Any

class FinishedView:
    def __init__(
            self,
            window: tk.Tk
        ) -> None:
        self.window = window
        self.frame = tk.Frame(window)
        self.label = tk.Label(self.frame, text="ダウンロードが終了しました。")
        self.label.pack(pady=10)

        self.button = tk.Button(self.frame, text="終了", command=self.on_button_pressed)
        self.button.pack(pady=10)

    def on_button_pressed(self) -> None:
        self.frame.pack_forget()
        # close the window
        self.window.destroy()