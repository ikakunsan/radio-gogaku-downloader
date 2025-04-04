# radio-gogaku-downloader

## 説明
NHKラジオ語学講座のストリーミングファイルをダウンロードするためのツールです。らじる★らじるの聞き逃しサービスを利用しています。

GUI不要で、コマンドラインのみで動作しますので、Linuxサーバー等でcronで定期実行させられます。

講座一覧はJSONファイルの形 (courses-all.json) でツール本体とは分離しています。

ファイル名等で日本語を取り扱う関係で、Linuxの場合はencodingをUTF-8にする必要があります。（注意事項参照）

音声はMP3に変換されます。デフォルトは128kbps。音質 (ビットレート) はオプションで変更できます。(64kbps / 128kbps / 256kbps が選択可。128kbpsが多分ベスト)

Windows 10/11 (64bit)では、windowsの下の実行ファイルに変換したものを使ってください。

◆◆◆ (2024/12/01) サーバー側のディレクトリ名変更に対応いました。
また、一部エラー対策を追加しました。
初回使用時のバグ修正しました。(Thanks @takushi1969)

v2.8以降で、Windows Defenderが、ダウンロードしたzipファイルをトロイの木馬に感染していると誤検出する問題があります。
（tar.gzは引っかからないし、unzipしたものも引っかかりません。再度zipにしたものも引っかかりません）
将来的にWindows Defenderの定義ファイルのアップデートで直ると思いますが、暫定的な対応として、zipディレクトリに手元で展開・圧縮したv2.8.1のzipファイルを置きました。

◆◆◆ (2024/5/12) GUIのフロントエンドを用意しました。（Ubuntu 22.04だと少しふるまいが変です。
ウィンドウが開けば動作自体には影響ないようです。Flet由来の問題かと思われます）

◆◆◆ ffmpeg 4.3以降でも動くように対策しました。(Thanks @ichinomoto for finding a workaround)
使おうとしているffmpegのバージョンが 4.3以降であれば、 "http_seekable" を無効にするオプション (-http_seekable 0) を付加します。

## 実行環境
- Python 3.xの走る環境。 (3.10で動作確認)
Linux（含むWSL）。たぶんMacOSも可。
- Windows10/11 64bit。 (Python等のインストールは不要。ffmpegのみ別途必要。詳細は注意事項参照）

#### その他必要なプログラム（Windows以外。あらかじめインストールしておいてください）
- python3-pip
- ffmpeg (注5)

#### 必要なPythonパッケージ (Windows以外。あらかじめpip3 installでインストールしておいてください)
- requests
- npyscreen
- ffmpeg-python
- flet  (GUI使用の場合)
- libmpv1  (GUI使用の場合)

## 使い方 (radigo-gui.py)
radigo-gui.py を実行。radio-gogaku-downloader のフロントエンドなので、
本体の radio-gogaku-downloader を同じディレクトリに置く必要があります。
設定項目は、courses-selected.json に保管されます。
(courses-selected.jsonは、コマンドライン版と互換です)

## 使い方 (radio-gogaku-downloader.py)
コマンドラインから実行。（Windows以外。Windowsでの使用法は注意事項参照）

    radio-gogaku-downloader.py [-h] [-s] [-q] [-p] [-y] [-d DIR] [-o OUTPUT]

cronでの実行例 （一般ユーザーで実行。ビットレート128kbps。サンプリングレート44.1kHz。毎日11:00に実行。2022年度からサーバーへのファイルのアップロードのタイミングが毎週月曜日から毎日放送後に変更になったため、毎日走らせるのがいいかと思います）

    00 11 * * *   /home/ikakunsan/bin/radio-gogaku-downloader.py -q1 -p1 -d /mnt/win/gogaku

### オプション

#### -h, --help
ヘルプの表示

#### -s, --select
講座選択画面の表示。
最初の起動時などcourses-selected.jsonが存在しないときには、このオプションを選択しなくても講座選択画面に進みます。
矢印キー、Tabキーで移動、スペースバーで選択の切り替えです。
必要な講座にチェックを入れ、OKのところでEnterを押すと、プログラムと同じディレクトリにcourses-selected.jsonというファイルを作ります。

#### -d DIR, --dir DIR
音声ファイルを保存する際のルートディレクトリの指定。
音声ファイルはここで示したディレクトリの下のサブディレクトリに格納されます。
-h, -s を指定したとき以外は必須です。音声をダウンロードする場合は、必ず指定してください。

#### -q QUALITY, --quality QUALITY
MP3のビットレートを0から2までの数字で指定。0: 64kbps (basic), 1: 128kbps (high), 2: 256kbps (best)。
デフォルトは1 (128kbps)。（数字の前の空白はあってもなくても可）
15分の放送でのファイルサイズは、64kbpsで約7MB、128kbpsで約14MB、256kbpsで約28MBとなります。
64kbpsだと少し歪みがあります (AM放送並の品質)。128kbsだと音質はかなり向上します。256kbpsと128bpsの音質の差は小さい (ほとんど差がない) 印象です。
サイズとの兼ね合いでお好みで。

#### -p SAMPLE, --sample SAMPLE
MP3のサンプリングレートを選択。0: 48kHz, 1: 44.1kHz。
デフォルトは0 (48kHz)。（数字の前の空白はあってもなくても可）

#### -y YEAR, --year YEAR
ファイル名の放送日に年を加えるかの指定。0:年表示なし 1:年表示あり。デフォルトは1(年表示あり)。
ver 1 同様に月日のみのファイル名にする場合は 0 を指定。

#### -o OUTPUT, --output OUTPUT
保存ディレクトリ名、ファイル名のオプション。OUTPUTには、以下の1～4のいずれかを指定してください。このオプションがない場合は、1を指定したものとみなします。

1. 指定したディレクトリ/年度/講座名/日付.mp3
1. 指定したディレクトリ/年度/講座名/講座名_日付.mp3
1. 指定したディレクトリ/年度/講座名_日付.mp3
1. 指定したディレクトリ/講座名/年度/日付.mp3

#### -f, --force
強制上書き。デフォルトでは、すでに同名のファイルが存在した場合は上書きしません。
このオプションを付けると、既存の同名のファイルがあった場合に上書きします。

#### -V, --version
バージョン表示

## 注意事項
### その1
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

### その2
ストリーミングのファイルは毎週月曜日に前の週の内容に更新され、その際にそれ以前のファイルは消されます。
~~ただ、ボキャブライダーだけは、過去のファイルは削除されずに追加だけされています。
そのため、初回および強制上書きオンにすると非常に多くのファイル（2017年度以降すべて）がダウンロードされます。
これはサイト側の仕様なのでご容赦ください。~~ (2024.4 過去のファイルは削除され、ダウンロード期間は他と同じになりました)

### その3
Windowsでの使用について。
- GUIを用意しました。Windowsの環境では、こちらのほうが使い勝手がいいかと思います。
ダウンロードを開始すると、別ウィンドウでダウンロードの状態が表示されます。
（radio-gogaku-downloader.exeを起動しているので、その画面です）
- 実行に必要なファイル一式（ffmpeg.exeを除く）は、windowsディレクトリの下にあります。
- PowerShellもしくはコマンドプロンプトから動かせます。バッチファイルとそのショートカットを作って適当なところに置いておけば、
  ダブルクリックだけで実行できて便利かと思います。詳細はwindowsディレクトリのREADME.txtを参照してください。
- Python 3およびライブラリのインストールは不要です。
- ffmpeg.exeをパスの通ったところ、もしくは作業フォルダ (radio-gogaku-downloader.exeと同じフォルダ) に置きます。
  - https://www.gyan.dev/ffmpeg/builds/ （古いパッケージは置かなくなってしまったようです）
    ffmpeg-4.3.2-2021-02-27-full_build.7z で動作確認しています。新しめのものをダウンロードして、7zip等で展開してください。
    色々なファイルが入っていますが、必要なのはffmpeg.exeだけです。
- 使用しているモジュール (npyscreen) の関係で、PowerShellやコマンドプロンプト上では -s オプションでメニューの文字が重なって表示されます。(動作そのものは問題ありません)
  (WSL上での表示は正常ですします)
  これだと読めないという場合の番組選択の代替の方法については、windowsディレクトリのREADME.txtをご参照ください。

### その4
データ欠損対策。サイトからのダウンロードは複数のセグメントに分けて行うのですが、サーバー側の問題で、たまに一部のセグメントでエラー (HTTP 404) が発生してデータが欠損する事があります。V2.5でその対策を入れました。欠損があったと判断した場合は最大5回までリトライします。(回数を変えたいときは RETRY_MAX の数字を書き換えてください)
最大回数試みてエラーが消えないときは、最後に落としたもののファイル名に (incomplete) を追加します。
サーバーの調子でエラーの出やすいときがありますので、リトライしてもエラーが解消されないときは時間をずらして再度試みるといいかもしれません。

### その5
ffmpeg 4.3 以降で動かすための (暫定?) 対策 (4.3から追加された "http_seekable" を無効にする) が見つかり、適用しました。ffmpeg のバージョンを判別して、4.3以降であれば自動でオプション (-http_seekable 0) を付加します。

ffmpegを実行可能なffmpegを本スクリプトと同じディレクトリに置くと、そちらを優先して使う仕様はそのままです。
また何かあったときに、逃げ道として使うことがあるかも (?)。
Windows版には私のビルドした4.2.7の実行ファイルを添付しています。(少しの間残しておきます)

### その6
2024年4月に番組情報のJSON関係で変更があり、それに伴いcourses-*.jsonファイルの先頭数行を変更しました。従来のcourses-selected.jsonそのままだとエラーになりますので、新しいcourses-all.jsonをベースにcourses-selected.jsonを作り直してください。（古いものに "url_json" の行をコピペするのでも大丈夫です）

## 履歴

### V2.8.2
- 2025年度4月期対応。(終了した番組を除いたのと、一部番組名を変更しただけ。今年度は新規の番組は無し)

### V2.8.1
- 初回のcourses-selected.json作成時のバグ修正 (thanks a lot: @takushi1969)

### V2.8
- サーバーのディレクトリ名が変わったのでその対応。
- サーバー側の番組情報(開始・終了時刻)が間違っていたときの対策と一部の仕様変更に対応。

### V2.7.1
- バージョン表示追加
- GUIのフロントエンド追加

### V2.7
- 2024年度からの、NHKのJSONサイトのURL、サイト構成、JSONの内容変更に対応。（2024年4月時点では従来のサイトも併存しているので従来のバージョンも動作しますが、ゆくゆくは新サイトのみになるはず）
- 上記対応に伴い、courses-*.jsonの最初の数行を変更。
- courses-all.jsonを2024年度4月期に対応。（ヨーロッパ系言語の基礎と応用が1つのフォルダに統合）

### V2.6.1
- ffmpeg 4.3以降でも正常にダウンロードするための対策を追加。(使おうとしているffmpegを判別して、バージョンが 4.3以降であれば、自動で "http_seekable" を無効にするオプション (-http_seekable 0) を付加します)

### V2.6
- 本スクリプトと同じディレクトリに実行可能なffmpegがあれば、そちらを優先して使うようにした。
- その他細かい修正

### V2.5.1
- データ欠損発生時のファイル名変更のバグ修正
- その他細かい修正

### V2.5
- たまにデータが欠損する問題の対策。（セグメント単位でランダムに発生するHTTP 404エラーが原因。エラー発生時にリトライするようにした）（やっと！）
- 音質 (-q オプション) のデフォルトを 128kbps (-q 1) に変更。64kbpsは音質がいまいちなので。
- コマンドラインオプションでサンプリングレートを選択できるようにしました。48kHz (デフォルト）と44.1kHzから選べます。

### V2.4.2.2
- Windows版の修正&アップデート

### V2.4.2.1
- 2022年度前期番組対応
- 書式の修正。
- ログ機能追加。
- ネットワークエラーでダウンロードしたファイルが不完全になる問題の対策
- 予備で入れている番組情報のjsonは、2021-2が2021年度後期、2022-1が2022年度前期です。

### V2.4.1.1
- Windows版のアップデートがなされていなかったので修正。

### V2.4.1
- 2021年後期対応。
- "ラジオで！カムカムエヴリバディ" に対応

### V2.4
- いろいろな問題の修正（主にWindows環境）

### V2.3
- 音質（出力ファイルのビットレート）選択のオプション追加。

### V2.2.2
- 「ポルトガル語入門」の講座名とアドレスが間違っていたので訂正。

### V2.2.1
- Windows用に実行ファイルを追加。Python3のインストールは不要に。

### V2.2.0
- Windowsの限定サポート。courses-xxxx.jsonをマニュアルで編集しやすいように少し変更。

### V2.1.1
- 新講座が3月中に放送開始の場合、3月放送分が前の年度に扱われてしまう問題への対応。

### V2.1
- 2021年度前期の講座が正式に決まったので、番組一覧を訂正。
- プログラムを更新、course-all.jsonの中に連番で入れていた数字を廃止。

### V2.0.1
- 番組一覧を2021年度前期の講座内容に合わせて更新。

### V2.0
- 2021年度から元サイトの情報管理がXMLベースからJSONベースに変更になるので、それに合わせた変更。
- 「年度」情報はcourses-all.jsonからでなく、サイトのJSONから取るように変更。（放送する講座に変更がない限り年度頭でcourses-all.jsonの更新の必要なし）
- ファイル名が放送日の「月+日」だったのを「年+月+日」に変更。（オプション -y でv1同様年抜きにするのも可能）
- 出力のディレクトリ構成のバリエーション追加。

### V1.0
- 最初のバージョン。
## TODO
- ~~Windows用講座選択メニューのGUI化 (Tkinter)  ← 検討はしてます。TKinterは見た目がアレなので、別のもので。本体は今のままでGUIのフロントエンドを用意するつもり。~~

## その他
ミスで、過去のスターなど消してしまいました…。:cry:

ライセンスは一応入れていますが、結果に責任持ちませんぐらいの意味合いです。
