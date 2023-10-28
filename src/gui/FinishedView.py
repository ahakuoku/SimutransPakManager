import tkinter as tk
from typing import Any

class FinishedView:
    def __init__(
            self,
            window: tk.Tk,
            progress_log: str,
            error_description: (str | None)
        ) -> None:
        self.window = window
        self.frame = tk.Frame(window)
        if error_description:
            label_text = "エラーが発生しました。"
        else:
            label_text = "ダウンロードが終了しました。"
        self.label = tk.Label(self.frame, text=label_text)
        self.label.pack(pady=10)

        self.text_box = tk.Text(self.frame, height=10, state=tk.NORMAL)
        self.text_box.insert(tk.END, progress_log)
        if error_description:
            self.text_box.insert(tk.END, error_description)
        self.text_box.config(state=tk.DISABLED)
        self.text_box.pack(pady=10)

        self.button = tk.Button(self.frame, text="終了", command=self.on_button_pressed)
        self.button.pack(pady=10)

    def on_button_pressed(self) -> None:
        self.frame.pack_forget()
        # close the window
        self.window.destroy()