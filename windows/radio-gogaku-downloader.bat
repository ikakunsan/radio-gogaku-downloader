@echo off
REM
REM Windows用バッチファイルサンプル
REM
REM 【使い方】
REM  1. この一番下の行の -d 以降を自分に合うように書き換える。
REM  2. このバッチファイルのアイコンを右クリックしてショートカットを作成。
REM  3. ショートカットのアイコンを右クリックして名前を好きなように書き換える。
REM  4. ショートカットのアイコンをデスクトップ等好きな場所に置く。
REM  5. ショートカットのアイコンをダブルクリックで実行。
REM  6. 実行時にウィンドウを開きたくないなら、ショートカットのアイコンを右クリックして
REM     プロパティを開き、「実行時の大きさ」から「最小化」を選択して、OKボタンを押す。
REM
REM 【-dの書き方（ダウンロード先）の例】
REM
REM -d download    ← 現在のフォルダの下のdownloadというフォルダ（無い場合は自動作成）
REM -d C:\Users\XXXX\Music\Gogaku    ← XXXXはユーザー名。「ミュージック」フォルダの下の
REM                                     Gogakuというフォルダ（無い場合は自動作成）
REM -d C:/Users/XXXX/Music/Gogaku    ← 上と同じ（\でも/でもよい）


radio-gogaku-downloader.exe -d download
