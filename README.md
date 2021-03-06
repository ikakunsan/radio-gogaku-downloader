# radio-gogaku-downloader

## 説明
NHKラジオ語学講座のストリーミングファイルをダウンロードするためのツールです。

GUI不要で、コマンドラインのみで動作します。
講座一覧はJSONファイルの形でツール本体とは分離しています。
ファイル名等で日本語を取り扱う関係で、Linuxの場合はencodingをUTF-8にする必要があります。（注意事項参照）
音声は、64kbpsのMP3に変換されます。

## 実行環境
python 3.xの走る環境。
Linux（含むWSL。たぶんMacOSも可）。
なお、Windowsのコマンドプロンプトでは動きません。（WSL上では動作します）

#### その他必要なプログラム（あらかじめインストールしておいてください）
- python3-pip
- ffmpeg

#### 必要なPythonパッケージ (あらかじめpip3 installでインストールしておいてください)
- requests
- npyscreen
- ffmeg-python

## 使い方
コマンドラインから実行。

    radio-gogaku-downloader.py [-h] [-s] [-d DIR] [-o OUTPUT]

### オプション

#### -h, --help
ヘルプの表示

#### -s, --select
講座選択画面の表示。
最初の起動時などcourses-selected.jsonが存在しないときには、このオプションを選択しなくても講座選択画面に進みます。
必要な講座にチェックを入れ、OKを押すと、プログラムと同じディレクトリにcourses-selected.jsonというファイルを作ります。

#### -d DIR, --dir DIR
音声ファイルを保存する際のルートディレクトリの指定。
音声ファイルはここで示したディレクトリの下のサブディレクトリに格納されます。
-h, -s を指定したとき以外は必須です。音声をダウンロードする場合は、必ず指定してください。

#### -o OUTPUT, --output OUTPUT
保存ディレクトリ名、ファイル名のオプション。OUTPUTには、以下の1～3のいずれかを指定してください。このオプションがない場合は、1を指定したものとみなします。

1. 指定したディレクトリ/年度/講座名/日付.mp3
1. 指定したディレクトリ/年度/講座名/講座名_日付.mp3
1. 指定したディレクトリ/年度/講座名_日付.mp3

#### -f, --force
強制上書き。デフォルトでは、すでに同名のファイルが存在した場合は上書きしません。
このオプションを付けると、既存の同名のファイルがあった場合に上書きします。

## 注意事項
### その1
使用しているモジュールの関係でWindowsネイティブ環境では動きません。（WSL上でなら動作します）

### その2
Linux環境で、下記のようなエラー（ロケールや文字コードに関係ありそうなエラー）が出る場合、encodingがUTF-8になっていません。
（このツールの実行には、encodingをUTF-8にする必要があります。 Linuxのみ。Windows (WSL)やMac OSでは出ないはず）

- UnicodeDecodeError: 'ascii' codec can't decode byte 0xe5 in position 147: ordinal not in range(128)
- locale.Error: unsupported locale setting

```
$ locale
```
と打ってみて、出力された中でLANGに"UTF-8"の文字が含まれていればエラーは出ないはずです。
設定例として、例えば、~/.bashrcの最後に以下を追加するとか。
要はencodingがUTF-8になっていればやり方は問いませんので、お好みのやり方で。
```
export LANG=C.UTF-8
export LANGUAGE=en_US:en   <-- エラーメッセージ等日本語にしたい人は不要
```

### その3
ストリーミングのファイルは毎週月曜日に前の週の内容に更新され、その際にそれ以前のファイルは消されます。
ただ、ボキャブライダーだけは、過去のファイルは削除されずに追加だけされています。
そのため、初回および強制上書きオンにすると非常に多くのファイル（2017年度以降すべて）がダウンロードされます。
これはサイト側の仕様なのでご容赦ください。
