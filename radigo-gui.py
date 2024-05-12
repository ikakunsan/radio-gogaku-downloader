#!/usr/bin/env python3
#
# GUI frontend for NHK radio gogaku downloader
#
# 2024 ikakunsan
# https://github.com/ikakunsan/radio-gogaku-downloader
#
#
import os
import sys
from pathlib import Path
import flet as ft
import json
import math
import time
import subprocess

################################
VERSION = "2024-0512"
PATH_ALL = "courses-all.json"
PATH_SEL = "courses-selected.json"
SUB_PROC_NAME = "radio-gogaku-downloader"
if os.name == "nt":  # = Windows
    SUB_PROC_NAME += ".exe"
else:
    SUB_PROC_NAME += ".py"

APP_TITLE = "RadiGo"
APP_WIDTH = 880
APP_HEIGHT = 620
CB_COLUMNS = 3

FOLDER_SEL_BUTTON_TEXT = "フォルダ選択"

################################

app_params = {
    "save_dir": "",
    "path_format": 1,
    "quality": 1,
    "sample_rate": 0,
    "year": 1,
    "force_overwrite": 0,
    "theme_mode": 0,
    "terminated": 0,
}


def create_selected_file(filepath, json_all):
    print("Creating selected file base")
    sel = dict(
        year=json_all["year"],
        url_json=json_all["url_json"],
        programs=list(),
        gui_settings=app_params,
    )
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sel, f, indent=4, ensure_ascii=False)
        r = True
    except:
        r = False
    return r


def update_selected_file(json_sel, filepath):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_sel, f, indent=4, ensure_ascii=False)
        r = True
    except:
        r = False
    return r


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.title = APP_TITLE
    page.window_width = APP_WIDTH
    page.window_height = APP_HEIGHT
    page.window_resizable = False
    downloadable = True  # for future use
    path_prog_all = Path(PATH_ALL)
    path_prog_sel = Path(PATH_SEL)
    cb_width = int((APP_WIDTH - 10 * (CB_COLUMNS + 1)) / CB_COLUMNS)
    startbutton_txt = "ダウンロード開始"
    json_prog_all = {}
    json_prog_sel = {}

    def open_json_not_found_dlg():
        page.dialog = dlg_json_not_found
        dlg_json_not_found.open = True
        page.update()

    def close_json_not_fount_dlg_clicked(e):
        dlg_json_not_found.open = False
        page.update()
        page.window_close()

    btn_close_json_not_found_dlg = ft.FilledButton(
        text="    OK    ",
        on_click=close_json_not_fount_dlg_clicked,
    )

    dlg_json_not_found = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"{PATH_ALL}が見つかりません"),
        content=ft.Text(
            f"{PATH_ALL}を、このプログラムと同じフォルダに置いてください"
        ),
        actions=[
            btn_close_json_not_found_dlg,
        ],
    )

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        dir_current = Path(sys.argv[0]).resolve().parent
    else:
        dir_current = Path(__file__).resolve().parent
    path_prog_all = dir_current / path_prog_all
    path_prog_sel = dir_current / path_prog_sel

    try:
        with open(path_prog_all, "r", encoding="utf-8") as fall:
            json_prog_all = json.load(fall)
    except:
        print(f"[ERROR] Cannot open {path_prog_all}")
        open_json_not_found_dlg()

    try:
        with open(path_prog_sel, "r", encoding="utf-8") as fsel:
            json_prog_sel = json.load(fsel)
        try:
            # もしGUI対応でなくsettingsの項目がなかったら追加する。
            json_prog_sel["gui_settings"]
        except:
            print("[WARNING] GUI settings not found. Create with default values")
            json_prog_sel["gui_settings"] = app_params
            update_selected_file(json_prog_sel, path_prog_sel)
    except:
        print(f"[WARNING] {path_prog_sel} is missing or broken.")
        json_prog_sel = create_selected_file(path_prog_sel, json_prog_all)

    if json_prog_sel["gui_settings"]["theme_mode"] == 0:
        page.theme_mode = ft.ThemeMode.SYSTEM
    elif json_prog_sel["gui_settings"]["theme_mode"] == 1:
        page.theme_mode = ft.ThemeMode.LIGHT
    elif json_prog_sel["gui_settings"]["theme_mode"] == 2:
        page.theme_mode = ft.ThemeMode.DARK

    course_count = len(json_prog_all["programs"]) - 1

    def if_any_courses_checked(itemlist):
        r = False
        for i in range(len(itemlist)):
            r = r or itemlist[i].value
        return r

    def print_size(e):
        print(f"page width={page.width}, height={page.height}")

    #################################################
    # Component groups
    #
    def line_top():  # Setting button only
        r = ft.Row(
            controls=[
                btn_settings,
                ft.Text(value=f"Ver. {VERSION}", color=ft.colors.GREY_500),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        return r

    def line_courses():
        global cb_course

        course_cols = CB_COLUMNS
        course_rows = math.ceil(course_count / course_cols)

        i = 0
        cb_table = []

        for r in range(course_rows):
            onerow = []
            for c in range(course_cols):
                if i < course_count:
                    onerow.append(cb_containers[r * 3 + c])
                i += 1
            cb_table.append(ft.Row(controls=onerow))

        r = ft.Column(controls=cb_table)
        return r

    def line_dir_select(downloadable):  # TextField and folder select button
        return ft.Row(controls=[tf_savedir, btn_savedir])

    def line_start_button(downloadable):  #
        r = ft.Row(
            controls=[
                btn_start,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        return r

    def settings_all():
        global app_params

        def quality_changed(e):
            json_prog_sel["gui_settings"]["quality"] = int(e.control.value)
            update_selected_file(json_prog_sel, path_prog_sel)

        def sample_rate_changed(e):
            json_prog_sel["gui_settings"]["sample_rate"] = int(e.control.value)
            update_selected_file(json_prog_sel, path_prog_sel)

        def year_fn_changed(e):
            json_prog_sel["gui_settings"]["year"] = int(e.control.value)
            update_selected_file(json_prog_sel, path_prog_sel)

        def path_fmt_changed(e):
            # print(type(e.control.value))
            json_prog_sel["gui_settings"]["path_format"] = int(e.control.value) + 1
            update_selected_file(json_prog_sel, path_prog_sel)

        def force_overwrite_changed(e):
            json_prog_sel["gui_settings"]["force_overwrite"] = int(e.control.value)
            update_selected_file(json_prog_sel, path_prog_sel)

        def theme_mode_changed(e):
            tm = int(e.control.value)
            if tm == 0:
                page.theme_mode = ft.ThemeMode.SYSTEM
            elif tm == 1:
                page.theme_mode = ft.ThemeMode.LIGHT
            elif tm == 2:
                page.theme_mode = ft.ThemeMode.DARK
            page.update()
            json_prog_sel["gui_settings"]["theme_mode"] = int(e.control.value)
            update_selected_file(json_prog_sel, path_prog_sel)

        quality = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(value=0, label="64kbs (低音質)"),
                    ft.Radio(value=1, label="128kbs (高音質)"),
                    ft.Radio(value=2, label="256kbs (最高音質)"),
                ]
            ),
            value=json_prog_sel["gui_settings"]["quality"],
            on_change=quality_changed,
        )
        sample_rate = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(value=0, label="48kHz"),
                    ft.Radio(value=1, label="44.1kHz"),
                ]
            ),
            value=json_prog_sel["gui_settings"]["sample_rate"],
            on_change=sample_rate_changed,
        )
        year_fn = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(value=0, label="月日のみ"),
                    ft.Radio(value=1, label="年月日"),
                ]
            ),
            value=json_prog_sel["gui_settings"]["year"],
            on_change=year_fn_changed,
        )
        path_fmt = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(value=0, label="(指定したフォルダ)/年度/講座名/日付.mp3"),
                    ft.Radio(
                        value=1,
                        label="(指定したフォルダ)/年度/講座名/講座名_日付.mp3",
                    ),
                    ft.Radio(value=2, label="(指定したフォルダ)/年度/講座名_日付.mp3"),
                    ft.Radio(value=3, label="(指定したフォルダ)/講座名/年度/日付.mp3"),
                ]
            ),
            value=json_prog_sel["gui_settings"]["path_format"] - 1,
            on_change=path_fmt_changed,
        )
        if json_prog_sel["gui_settings"]["force_overwrite"] == 0:
            ow = False
        else:
            ow = True
        force_overwrite = ft.Checkbox(
            label="強制上書き",
            value=ow,
            on_change=force_overwrite_changed,
        )
        theme_mode = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(value=0, label="システムに合わせる"),
                    ft.Radio(value=1, label="ライトモード"),
                    ft.Radio(value=2, label="ダークモード"),
                ]
            ),
            value=json_prog_sel["gui_settings"]["theme_mode"],
            on_change=theme_mode_changed,
        )
        hspacer = ft.Container(height=10)
        r = ft.Column(
            [
                ft.Tooltip(
                    message="お薦めは128kbps（256kbpsと音質差はほぼ無し）",
                    content=ft.Text(
                        "音質             ", theme_style=ft.TextThemeStyle.TITLE_MEDIUM
                    ),
                    prefer_below=False,
                    show_duration=3000,
                ),
                quality,
                hspacer,
                ft.Tooltip(
                    message="MP3のサンプリングレート。特にこだわりが無ければ48kHzで",
                    content=ft.Text(
                        "サンプリング周波数", theme_style=ft.TextThemeStyle.TITLE_MEDIUM
                    ),
                    prefer_below=False,
                    show_duration=3000,
                ),
                sample_rate,
                hspacer,
                ft.Tooltip(
                    message="ファイル名の日付部分に年を含めるかどうかの設定",
                    content=ft.Text(
                        "ファイル名の日付部分の構成",
                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    ),
                    prefer_below=False,
                    show_duration=3000,
                ),
                year_fn,
                hspacer,
                ft.Tooltip(
                    message="保存の際のフォルダとファイル名の構成",
                    content=ft.Text(
                        "保存フォルダ・ファイル名の構成",
                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    ),
                    prefer_below=False,
                    show_duration=3000,
                ),
                path_fmt,
                hspacer,
                ft.Tooltip(
                    message="同名のファイルがあったときに上書き保存するかどうか。ファイルが壊れていたときのリカバリー用",
                    content=ft.Text(
                        "強制上書き保存（前回中断したときにはチェック）",
                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    ),
                    prefer_below=False,
                    show_duration=3000,
                ),
                force_overwrite,
                hspacer,
                ft.Tooltip(
                    message="ライトモード、ダークモードの切り替え",
                    content=ft.Text(
                        "ダークモード設定", theme_style=ft.TextThemeStyle.TITLE_MEDIUM
                    ),
                    prefer_below=False,
                    show_duration=3000,
                ),
                theme_mode,
            ]
        )
        return r

    def route_change(route):
        # page.on_resize = print_size
        page.views.append(
            ft.View(
                "/",
                [
                    line_top(),
                    ft.Container(height=10),
                    line_courses(),
                    ft.Container(height=14),
                    line_dir_select(downloadable),
                    ft.Container(height=14),
                    line_start_button(downloadable),
                ],
            )
        )
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [
                        ft.AppBar(
                            title=ft.Text("設定"),
                        ),
                        settings_all(),
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    #################################################
    # Component event handlers
    #
    def sw_lock_changed(e):
        pass

    # def open_json_not_found_dlg():
    #     page.dialog = dlg_json_not_found
    #     dlg_json_not_found.open = True
    #    page.update()

    # def close_json_not_fount_dlg_clicked(e):
    #     dlg_json_not_found.open = False
    #     page.update()
    #     page.window_close()

    def cb_course_changed(e):
        list_programs = []
        for i in range(course_count):
            if cb_course[i].value:
                list_programs.append(json_prog_all["programs"][i])
        list_programs.append(json_prog_all["programs"][course_count])
        json_prog_sel["programs"] = list_programs
        if if_any_courses_checked(cb_course) and len(tf_savedir.value) > 0:
            btn_start.disabled = False
        else:
            btn_start.disabled = True
        btn_start.update()
        update_selected_file(json_prog_sel, path_prog_sel)

    def store_selected_folder(e: ft.FilePickerResultEvent):
        global app_params

        if e.path:
            tf_savedir.value = e.path
            tf_savedir.update()
            json_prog_sel["gui_settings"]["save_dir"] = e.path
        if if_any_courses_checked(cb_course) and len(tf_savedir.value) > 0:
            btn_start.disabled = False
        else:
            btn_start.disabled = True
        btn_start.update()
        update_selected_file(json_prog_sel, path_prog_sel)

    def savedir_changed(e):
        if if_any_courses_checked(cb_course) and len(tf_savedir.value) > 0:
            btn_start.disabled = False
        else:
            btn_start.disabled = True
        btn_start.update()

    def start_clicked(e):
        open_app_running_dlg()

    def open_app_running_dlg():
        page.dialog = dlg_app_running
        dlg_app_running.open = True
        page.update()
        path_subprocess = str(dir_current / SUB_PROC_NAME)
        subprocess_params = [
            path_subprocess,
            "-d",
            json_prog_sel["gui_settings"]["save_dir"],
            "-o",
            str(json_prog_sel["gui_settings"]["path_format"]),
            "-q",
            str(json_prog_sel["gui_settings"]["quality"]),
            "-p",
            str(json_prog_sel["gui_settings"]["sample_rate"]),
            "-y",
            str(json_prog_sel["gui_settings"]["year"]),
        ]
        if json_prog_sel["gui_settings"]["force_overwrite"] == 1:
            subprocess_params += "-f"
        try:
            sp = subprocess.Popen(subprocess_params)
            # sp = subprocess.Popen(subprocess_params, stdout=subprocess.PIPE, universal_newlines=True, bufsize=0,)

            sp.wait()

            dlg_app_running.open = False
            page.dialog = dlg_app_finished
            dlg_app_finished.open = True
            page.update()
        except:
            open_app_not_found_dlg()

    def close_finish_dlg_clicked(e):
        dlg_app_finished.open = False
        page.update()

    def open_app_not_found_dlg():
        page.dialog = dlg_app_not_found
        dlg_app_not_found.open = True
        page.update()

    def close_app_not_fount_dlg_clicked(e):
        dlg_app_not_found.open = False
        page.update()

    #################################################
    # Component definitions
    #

    # btn_close_json_not_found_dlg = ft.FilledButton(
    #     text="    OK    ",
    #     on_click=close_json_not_fount_dlg_clicked,
    #)

    # dlg_json_not_found = ft.AlertDialog(
    #    modal=True,
    #     title=ft.Text(f"{PATH_ALL}が見つかりません"),
    #     content=ft.Text(
    #         f"{PATH_ALL}を、このプログラムと同じフォルダに置いてください"
    #     ),
    #     actions=[
    #         btn_close_json_not_found_dlg,
    #     ],
    # )

    btn_settings = ft.IconButton(
        icon=ft.icons.SETTINGS_OUTLINED,
        icon_color="grey800",
        tooltip="設定",
        on_click=lambda _: page.go("/settings"),
    )

    sw_lock = ft.Switch(label="選択ロック解除", value=False, on_change=sw_lock_changed)

    cb_course = [""] * course_count

    cb_containers = []
    for i in range(course_count):
        cb_course[i] = ft.Checkbox(
            label=json_prog_all["programs"][i]["title"],
            value=False,
            on_change=cb_course_changed,
        )
        cb_containers.append(
            ft.Container(
                content=cb_course[i],
                margin=0,
                padding=0,
                width=cb_width,
                height=30,
            )
        )
        for j in range(len(json_prog_sel["programs"]) - 1):
            # print(
            #     json_prog_all["programs"][i]["dir"], json_prog_sel["programs"][j]["dir"]
            # )
            if (
                json_prog_all["programs"][i]["dir"]
                == json_prog_sel["programs"][j]["dir"]
            ):
                cb_course[i].value = True

    tf_savedir = ft.TextField(
        label="保存フォルダ",
        hint_text="フォルダを選択してください",
        value=json_prog_sel["gui_settings"]["save_dir"],
        prefix="",
        read_only=True,
        expand=True,
        border_radius=ft.border_radius.all(10),
        on_change=savedir_changed,
    )

    btn_savedir = ft.OutlinedButton(
        text=f"   {FOLDER_SEL_BUTTON_TEXT}   ",
        style=ft.ButtonStyle(padding=20),
        tooltip=FOLDER_SEL_BUTTON_TEXT,
        on_click=lambda _: pick_folder_dialog.get_directory_path(
            dialog_title=FOLDER_SEL_BUTTON_TEXT
        ),
    )

    pick_folder_dialog = ft.FilePicker(on_result=store_selected_folder)
    page.overlay.append(pick_folder_dialog)

    btn_start = ft.FilledButton(
        text=f"      {startbutton_txt}      ",
        style=ft.ButtonStyle(padding=30),
        tooltip=startbutton_txt,
        disabled=True,
        on_click=start_clicked,
    )

    txt_download_status = ft.Text(value="")

    dlg_app_running = ft.AlertDialog(
        modal=True,
        title=ft.Text("ダウンロード実行中"),
        content=ft.Column(
            height=110,
            controls=[
                ft.Text(
                    "完了までお待ち下さい。(1講座あたり2～3分程度かかります)\n"
                    + "もし中断した場合は、次回は設定で強制上書きをONにしてください。\n"
                    + "（あとで元に戻すのをお忘れなく）"
                ),
                ft.Container(height=10),
                ft.ProgressBar(),
                ft.Container(height=10),
                txt_download_status,
            ],
        ),
    )

    btn_close_finish_dlg = ft.FilledButton(
        text="    OK    ",
        on_click=close_finish_dlg_clicked,
    )

    dlg_app_finished = ft.AlertDialog(
        modal=True,
        title=ft.Text("完了"),
        content=ft.Text("ダウンロードを完了しました"),
        actions=[
            btn_close_finish_dlg,
        ],
    )

    btn_close_app_not_found_dlg = ft.FilledButton(
        text="    OK    ",
        on_click=close_app_not_fount_dlg_clicked,
    )

    dlg_app_not_found = ft.AlertDialog(
        modal=True,
        title=ft.Text("実行ファイルが見つかりません"),
        content=ft.Text(
            f"{SUB_PROC_NAME}を、このプログラムと同じフォルダに置いてください"
        ),
        actions=[
            btn_close_app_not_found_dlg,
        ],
    )

    #################################################
    if if_any_courses_checked(cb_course) and len(tf_savedir.value) > 0:
        btn_start.disabled = False
    else:
        btn_start.disabled = True

    page.views.clear()
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=main, assets_dir="assets")
