
Windowsでの使い方

- 実行ファイル単体で動作します。ライブラリファイルは不要です。
- 実行ファイルと同じフォルダに、courses-selected.json が必要です。
- Windows上では-sオプションは使えません。（Windows用のcursesライブラリが
  日本語をサポートしていないため）

- ライセンスの関係で、ffmpegは同梱していません。インストールしていない場合
  は別途用意する必要があります。

【ffmpegの準備】
 1. ffmpegをダウンロード。
    https://www.gyan.dev/ffmpeg/builds/packages/ のreleaseの下にある
    ffmpeg-4.3.2-2021-02-27-full_build.7z で動作確認しています。
    これより新しいものであれば動くと思います。
    上記のページの、releaseの下にある適当なものをダウンロードします。
    essntial_build, full_buildのどれでも、7z, zipのいずれでもいいです。
    迷ったら、zipの中で一番上にあるものを選んでください。

 2. ダウンロードしたファイルを解凍。
    binというフォルダの下にffmpeg.exe (=ffmpeg)があります。
    他にもいろいろなファイルが入っていますが、必要なのはffmpeg.exeのみで
    す。

 2. ffmpeg.exeをパスの通ったところ、もしくは作業フォルダ 
    (radio-gogaku-downloader.exeと同じフォルダ) に置きます。


【番組リストの準備】
 1. courses-all.jsonをコピーして、コピーしたファイルをcourses-selected.json
    という名前に変更。
 2. courses-selected.jsonをメモ帳もしくはエディタで開き、不要な番組の入った
    行を削除。（不要な番組の行のみ削除して、それ以外はそのままにしておくこ
    と）
 3. 編集が終わったらファイルを保存。


【使い方】
 1. radio-gogaku-downloader.batの一番下の行の -d 以降を自分に合うように書き
    換える。
 2. radio-gogaku-downloader.batのアイコンを右クリックしてショートカットを作
    成。
 3. ショートカットのアイコンを右クリックして、名前を好きなように書き換える。
 4. ショートカットのアイコンをデスクトップ等好きな場所に置く。
 5. ショートカットのアイコンをダブルクリックで実行。
 6. もし実行時にウィンドウが開くのがいやなら、ショートカットのアイコンを右ク
    リックしてプロパティを開き、「実行時の大きさ」から「最小化」を選択して、
    OKボタンを押す。

【主なオプション】

[-qオプション (数字との間にスペースあってもなくてもよし)]
 -q 0   ← 64kbps MP3に変換（オプション無しの場合も同じ）
 -q 1   ← 128kbps MP3に変換
 -q 2   ← 256kbps MP3に変換

[-d オプション（ダウンロード先）の例]
 -d download    ← radio-gogaku-downloader.exeのあるフォルダの下のdownloadと
                   いうフォルダ（無い場合は自動作成）の中。
 -d C:\Users\XXXX\Music\Gogaku    ← (XXXXはユーザー名)「ミュージック」フォ
                   ルダの下のGogakuというフォルダ（無い場合は自動作成）の中
 -d C:/Users/XXXX/Music/Gogaku    ← 上と同じ（\でも/でもよい）
