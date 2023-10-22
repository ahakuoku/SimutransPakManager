import os
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable, Any

class SelectItemView:
    def __init__(
            self,
            window: tk.Tk,
            definition_json: Any, 
            show_progress_view: Callable[[Any, int, str], None] # [definition_json, selected_index, destination_path]
        ) -> None:
        self.frame = tk.Frame(window)
        self.show_progress_view = show_progress_view
        self.definition_json = definition_json
        self.pakset_names = [pakset["name"] for pakset in definition_json["paks"]]

        self.label = tk.Label(self.frame, text="ダウンロードするアイテムを選択してください")
        self.label.pack(pady=10)

        # ダウンロードするアイテムを選択するための変数
        self.selected_item = tk.IntVar(value=-1)

        # アイテムの一覧からラジオボタンを作成する
        for i, item in enumerate(self.pakset_names):
            radio = tk.Radiobutton(self.frame, text=item, variable=self.selected_item, value=i)
            radio.pack()

        # 次へボタンオブジェクトを作成
        self.button = tk.Button(self.frame, text="次へ", command=self.on_next_button_pressed)
        # 次へボタンオブジェクトを配置
        self.button.pack(pady=10)

        # 次へボタンが押されたときの処理
    def on_next_button_pressed(self) -> None:
        selected_index = self.selected_item.get()
        if selected_index == -1:
            messagebox.showwarning("未選択", "アイテムを選択してください！")
            return
        self.select_path_and_show_next_page(index=selected_index)

    def select_path_and_show_next_page(self, index: int) -> None:
        # open the directory selection dialog
        initialdir=os.path.abspath(os.path.dirname(__file__))
        definition_path = filedialog.askdirectory(initialdir=initialdir)
        # ファイルが選択された場合
        if definition_path:
            self.frame.pack_forget()
            self.show_progress_view(self.definition_json, index, definition_path)
        # ファイルが選択されなかった場合
        else:
            messagebox.showwarning("未選択", "ダウンロード先ディレクトリを選択してください！")