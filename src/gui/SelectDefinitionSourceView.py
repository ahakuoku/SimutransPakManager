import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Any

class SelectDefinitionSourceView:
    def __init__(self, window: tk.Tk, show_select_item_view: Callable[[Any], None]):
        self.frame = tk.Frame(window)
        self.show_select_item_view = show_select_item_view

        # 1ページ目の内容を作成
        self.label = tk.Label(self.frame, text="定義ファイルの取得方法を選択してください")
        self.label.pack(pady=10)

        # ローカルかネットワークかを選択するための変数
        self.source = tk.IntVar()

        # ラジオボタンオブジェクトを作成
        radio1 = tk.Radiobutton(self.frame, text="ローカルから読み込む", variable=self.source, value=1, anchor="w")
        radio2 = tk.Radiobutton(self.frame, text="ネットワークから取得する（未実装）", variable=self.source, value=2, anchor="w")

        # ラジオボタンオブジェクトを配置
        radio1.pack(pady=10)
        radio2.pack(pady=10)

        # 次へボタンオブジェクトを作成
        self.button = tk.Button(self.frame, text="次へ", command=self.on_next_button_pressed)
        # 次へボタンオブジェクトを配置
        self.button.pack(pady=10)

    # 次へボタンが押されたときの処理
    def on_next_button_pressed(self) -> None:
        # ローカルが選択されている場合
        if self.source.get() == 1:
            self.select_file_and_show_next_page()
        # ネットワークが選択されている場合
        elif self.source.get() == 2:
            # 未実装であることをメッセージボックスで表示
            messagebox.showinfo("未実装", "この機能はまだ実装されていません")
        # 何も選択されていない場合
        else:
            # 選択を促すメッセージボックスを表示
            messagebox.showwarning("選択してください", "定義ファイルの取得方法を選択してください")

    def select_file_and_show_next_page(self):
        # ファイル選択ダイアログを開く
        initialdir=os.path.abspath(os.path.dirname(__file__))
        definition_file_path = filedialog.askopenfilename(filetypes=[("JSONファイル", "*.json")], initialdir=initialdir)
        # ファイルが選択された場合
        if definition_file_path:
            with open(definition_file_path, "r", encoding="utf-8") as f:
                definition_json = json.load(f)
            # 1ページ目のフレームを非表示にする
            self.frame.pack_forget()
            # go to the next page
            self.show_select_item_view(definition_json)
        # ファイルが選択されなかった場合
        else:
            messagebox.showwarning("未選択", "定義ファイルを選択してください！")
