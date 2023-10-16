# 概要
pak構築作業を自動化するプログラムです。

# 実行方法
## 前提
- python version 3.11.6
- `pip install requests cabarchive`

## 実行
コマンドライン実行

```shell
python src/cmd_entry.py <インストール先ディレクトリ> <定義jsonファイル名> <何番目のpakset定義を実行するか>
```

(例) `python src/cmd_entry.py ~/simutrans/ pak-definitions.json 0`
