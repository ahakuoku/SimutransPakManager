import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from typing import Callable, Any

class DownloadProgressView:
    def __init__(
            self,
            window: tk.Tk
        ) -> None:
        self.frame = tk.Frame(window)
        self.label = tk.Label(self.frame, text="ダウンロード中です")
        self.label.pack(pady=10)

        self.text_box = tk.Text(self.frame, height=10, state=tk.DISABLED)
        self.text_box.pack(pady=10)

        self.progress_percent = tk.IntVar(value=0)

        # プログレスバーオブジェクトを作成
        self.progress_bar = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, length=200, maximum=100,mode='determinate', variable=self.progress_percent)

        # プログレスバーオブジェクトを配置
        self.progress_bar.pack(pady=10)

    def update_progress(self, progress_percent: int) -> None:
        # プログレスバーの値を設定
        self.progress_percent = progress_percent
        # ウィンドウを更新
        self.window.update_idletasks()

    def add_message(self, message: str) -> None:
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, message + "\n")
        self.text_box.config(state=tk.DISABLED)
        self.text_box.see(tk.END)
