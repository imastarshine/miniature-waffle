import src.tracker_analytics
import flet_audio as fta
import src.settings
import src.tracker
import flet as ft
import src.config
import threading
import hashlib
import ctypes
import time
import re
import os

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

INPUT_PATTERN = r"(\d{1,2}):(\d{1,2})"
LR_LOADFROMFILE = 0x00000010
IMAGE_ICON = 1
WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1

config = src.config.Config()
config.load()

tracker = src.tracker.Tracker()
tracker.load()


class CountdownThread(threading.Thread):
    def __init__(self, interval: int = 1, value: int = 10, on_update: callable = None, on_complete: callable = None):
        super().__init__(daemon=True)
        self.interval = interval
        self.stop_event = threading.Event()
        self.value = value
        self.initial_value = value
        self.on_update = on_update
        self.on_complete = on_complete
        self.chilling = False
        self._start_chilling_time = ""
        self.start_time = src.tracker.get_time()

    def run(self):
        while not self.stop_event.is_set():
            if not self.chilling:
                self.value -= 1
            if self.stop_event.wait(self.interval):
                self.on_complete(False)
                break
            if self.value == 0:
                self.on_complete(True)
                break
            if self.on_update and not self.chilling:
                self.on_update()

    def stop(self):
        self.stop_event.set()

    def chill(self):
        self.chilling = True
        self._start_chilling_time = src.tracker.get_time()

    def stop_chilling(self) -> str:
        self.chilling = False
        return self._start_chilling_time


def format_time(seconds: int):
    return time.strftime("%M:%S", time.gmtime(seconds))


def clamp(n, min_val, max_val):
    return max(min_val, min(n, max_val))


def zero_division(x0: int, x1: int):
    try:
        return x0 / x1
    except ZeroDivisionError:
        return 0


def change_app_icon(icon_path: str, app_name: str):
    HWND = ctypes.windll.user32.FindWindowW(None, app_name)

    if HWND == 0:
        return

    hIcon = ctypes.windll.user32.LoadImageW(
        0,
        icon_path,
        IMAGE_ICON,
        0,
        0,
        LR_LOADFROMFILE
    )

    if hIcon == 0:
        return

    ctypes.windll.user32.SendMessageW(HWND, WM_SETICON, ICON_SMALL, hIcon)
    ctypes.windll.user32.SendMessageW(HWND, WM_SETICON, ICON_BIG, hIcon)


def changer(icon_path: str, app_name: str):
    time.sleep(1)
    change_app_icon(icon_path, app_name)


def main(page: ft.Page):

    page.fonts = {
        "Epoch": "assets/fonts/Epoch.otf",
        "Montserrat-Medium": "assets/fonts/Montserrat-Medium.ttf",
        "Numerino-Curl": "assets/fonts/Numerino-Curl.otf",
        "Numerino-VenetoStencil": "assets/fonts/Numerino-VenetoStencil.otf",
        "Numerino-Wide": "assets/fonts/Numerino-Wide.otf",
    }

    page.theme = ft.Theme(
        color_scheme_seed=config.color_scheme,
        font_family="Montserrat-Medium"
    )

    page.theme_mode = config.theme_mode

    random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    page.title = f"Miniature Waffle | {random_hash}"

    page.spacing = 0
    page.padding = 0

    page.window.min_height = 540
    page.window.min_width = 480

    page.window.height = 540
    page.window.width = 480

    page.window.center()

    pick_files_dialog = ft.FilePicker()
    page.overlay.append(pick_files_dialog)

    tracker_watcher = src.tracker_analytics.TrackerWatcher(page, tracker)

    picker_id = 0
    rounds = 0
    current_mode = 1
    pomodoro_enabled = False

    mode_to_field = {
        1: "pomodoro_time",
        2: "short_break_time",
        3: "long_break_time"
    }

    countdown_thread: CountdownThread = None

    def easy_picker(pick_id: str, dialog_title: str = "Pick a file", file_type: ft.FilePickerFileType = None, allow_multiple: bool = False):
        nonlocal picker_id
        picker_id = pick_id
        pick_files_dialog.pick_files(
            dialog_title=dialog_title,
            file_type=file_type,
            allow_multiple=allow_multiple
        )

    def easy_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            path = e.files[0].path
            if picker_id == "background_image":
                config.background_image_path = path
                main_container.image.src = config.background_image_path
                src.settings.background_image.value = path
            elif picker_id == "notification_sound":
                config.notification_sound_path = path
                audio.src = config.notification_sound_path
                src.settings.notification_sound.value = path
            page.update()

    def on_pomodoro_update():
        progress_value = zero_division(countdown_thread.value, countdown_thread.initial_value)
        progress_time_input.value = format_time(countdown_thread.value)
        progress_time_ring.value = progress_value
        page.window.progress_bar = clamp(zero_division(1 - progress_value, 1), 0.022, 1)
        page.update()

    def on_pomodoro_complete(is_ended: bool):
        nonlocal pomodoro_enabled, rounds, current_mode
        pomodoro_enabled = False
        page.window.progress_bar = 0
        if is_ended:
            if current_mode == 1:
                tracker.add(src.tracker.DataType.focus, countdown_thread.start_time)
                if current_short_task.value:
                    tracker.add(src.tracker.DataType.short_task, countdown_thread.start_time, current_short_task.value)
            elif current_mode == 2:
                tracker.add(src.tracker.DataType.short_break, countdown_thread.start_time)
            elif current_mode == 3:
                tracker.add(src.tracker.DataType.long_break, countdown_thread.start_time)

        pomodoro_button.disabled = False
        short_break_button.disabled = False
        long_break_button.disabled = False
        state_button.tooltip = "Start"
        state_button.icon = ft.Icons.PLAY_ARROW
        stop_button.visible = False
        progress_time_input.read_only = False
        progress_time_input.value = format_time(getattr(config, mode_to_field[current_mode]))
        progress_time_ring.value = 0

        audio.src = "assets/sounds/success.mp3"
        audio.play()

        if rounds % 4 == 0 and rounds != 0:
            current_mode = 3
        else:
            if current_mode == 1:
                current_mode = 2
            else:
                current_mode = 1

        rounds += 1

        set_mode(current_mode)
        round_text.value = f"#{rounds}"
        page.update()

    def pomodoro_on_click(e: ft.ControlEvent):
        nonlocal countdown_thread, pomodoro_enabled
        if not pomodoro_enabled:
            pomodoro_enabled = True
            pomodoro_button.disabled = True
            short_break_button.disabled = True
            long_break_button.disabled = True
            state_button.tooltip = "Pause"
            state_button.icon = ft.Icons.PAUSE
            progress_time_input.read_only = True
            stop_button.visible = True

            countdown_thread = CountdownThread(
                interval=1,
                value=getattr(config, mode_to_field[current_mode]),
                on_update=on_pomodoro_update,
                on_complete=on_pomodoro_complete
            )
            countdown_thread.start()
        elif countdown_thread and countdown_thread.chilling:
            state_button.tooltip = "Pause"
            state_button.icon = ft.Icons.PAUSE
            current_time = src.tracker.get_time()
            chilling_start_time = countdown_thread.stop_chilling()
            tracker.add(
                src.tracker.DataType.pause,
                countdown_thread.start_time,
                chilling_start_time,
                current_time
            )
        else:
            state_button.tooltip = "Resume"
            state_button.icon = ft.Icons.PLAY_ARROW
            countdown_thread.chill()

        page.update()

    def stop_pomodoro(e: ft.ControlEvent):
        nonlocal pomodoro_enabled
        pomodoro_enabled = False
        pomodoro_button.disabled = False
        short_break_button.disabled = False
        long_break_button.disabled = False
        state_button.tooltip = "Start"
        state_button.icon = ft.Icons.PLAY_ARROW
        stop_button.visible = False
        progress_time_input.read_only = False
        progress_time_input.value = format_time(getattr(config, mode_to_field[current_mode]))
        progress_time_ring.value = 0
        on_pomodoro_complete(True)
        if countdown_thread:
            countdown_thread.stop()
            countdown_thread.join()
        page.update()

    def new_input(e: ft.ControlEvent):
        value = e.control.value

        # pattern matching
        if re.match(INPUT_PATTERN, value):
            try:
                minutes, seconds = map(int, value.split(":"))
                is_success = True
                if minutes > 59 or seconds > 59 or (minutes <= 0 and seconds < 0):
                    # TODO: show toast
                    is_success = False
                if is_success is True:
                    total_seconds = minutes * 60 + seconds
                    setattr(config, mode_to_field[current_mode], total_seconds)
                progress_time_input.value = format_time(
                    getattr(config, mode_to_field[current_mode])
                )
                progress_time_input.update()
            except ValueError:
                ...
        else:
            progress_time_input.value = format_time(
                getattr(config, mode_to_field[current_mode])
            )
            progress_time_input.update()

    def set_mode(new_mode: int):
        nonlocal current_mode
        current_mode = new_mode
        if current_mode == 1:
            progress_time_input.value = format_time(config.pomodoro_time)
            pomodoro_button.bgcolor = ft.Colors.ON_SECONDARY
            short_break_button.bgcolor = None
            long_break_button.bgcolor = None
        elif current_mode == 2:
            progress_time_input.value = format_time(config.short_break_time)
            pomodoro_button.bgcolor = None
            short_break_button.bgcolor = ft.Colors.ON_SECONDARY
            long_break_button.bgcolor = None
        elif current_mode == 3:
            progress_time_input.value = format_time(config.long_break_time)
            pomodoro_button.bgcolor = None
            short_break_button.bgcolor = None
            long_break_button.bgcolor = ft.Colors.ON_SECONDARY
        page.update()

    def pick_mode(e: ft.ControlEvent):
        nonlocal current_mode
        if pomodoro_enabled:
            return
        current_mode = e.control.data
        set_mode(current_mode)
        page.update()

    audio = fta.Audio(
        src=config.notification_sound_path,
        volume=zero_division(config.notification_sound_volume, 100)
    )

    current_short_task = ft.TextField(
        content_padding=ft.padding.symmetric(12, 12),
        border=ft.InputBorder.OUTLINE,
        height=48,
        border_radius=ft.border_radius.all(10),
        border_width=2,
        border_color=ft.Colors.SECONDARY_CONTAINER,
        focused_border_color=ft.Colors.PRIMARY,
        hint_text="Short task",
        max_length=50,
        text_align=ft.TextAlign.CENTER
    )

    pomodoro_button = ft.ElevatedButton(
        text="Pomodoro",
        bgcolor=ft.Colors.ON_SECONDARY,
        data=1,
        on_click=pick_mode
    )

    round_text = ft.Text(
        "#0",
        opacity=0.5
    )

    short_break_button = ft.ElevatedButton(
        text="Short Break",
        data=2,
        on_click=pick_mode
    )

    long_break_button = ft.ElevatedButton(
        text="Long Break",
        data=3,
        on_click=pick_mode
    )

    progress_time_ring = ft.ProgressRing(
        value=0,
        expand=True,
        width=170,
        height=170,
        stroke_width=9
    )

    progress_time_input = ft.TextField(
        value=format_time(config.pomodoro_time),
        text_align=ft.TextAlign.CENTER,
        text_style=ft.TextStyle(
            font_family="Numerino-Wide",
            size=44,
            weight=ft.FontWeight.BOLD
        ),
        border=ft.InputBorder.NONE,
        border_radius=0,
        border_width=0,
        width=170,
        max_length=5,
        read_only=False,
        on_submit=new_input
    )

    progress_time_background = ft.Container(
        width=200,
        height=200,
        border_radius=1000,
        bgcolor=ft.Colors.ON_SECONDARY
    )

    state_button = ft.ElevatedButton(
        text="Start",
        on_click=pomodoro_on_click,
        icon=ft.Icons.PLAY_ARROW
    )

    state_button = ft.IconButton(
        tooltip="Start",
        icon=ft.Icons.PLAY_ARROW,
        on_click=pomodoro_on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    stop_button = ft.IconButton(
        icon=ft.Icons.STOP,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        visible=False,
        on_click=stop_pomodoro
    )

    settings_button = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda e: page.open(src.settings.alert_dialog)
    )

    main_container = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Pomodoro Timer (⓿_⓿)",
                            text_align=ft.TextAlign.LEFT,
                            expand=True,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY
                        ),
                        src.tracker_analytics.analytics_button,
                        settings_button
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=2
                ),
                ft.Divider(),
                ft.Row(
                    [
                        pomodoro_button,
                        short_break_button,
                        long_break_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6
                ),
                ft.Stack(
                    controls=[
                        progress_time_background,
                        progress_time_ring,
                        progress_time_input
                    ],
                    alignment=ft.alignment.center,
                    expand=True
                ),
                round_text,
                current_short_task,
                ft.Divider(),
                ft.Row(
                    [
                        state_button,
                        stop_button
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=3
        ),
        expand=True,
        padding=10,
        image=ft.DecorationImage(
            src=config.background_image_path,
            fit=config.background_image_fit,
            opacity=zero_division(config.background_image_opacity, 100)
        )
    )

    # --=========== TRACKER ANALYTICS ===========-- #

    src.tracker_analytics.analytics_button.on_click = lambda e: tracker_watcher.on_open(tracker.data)

    # --=========== SETTINGS SETUP ===========-- #

    def on_settings_text_field_submit(e: ft.ControlEvent):
        if e.control.data == "background_image":
            config.background_image_path = e.control.value
            main_container.image.src = config.background_image_path
        elif e.control.data == "notification_sound":
            config.notification_sound_path = e.control.value
            audio.src = config.notification_sound_path
        elif e.control.data == "theme_color_scheme":
            config.color_scheme = e.control.value
            page.theme = ft.Theme(
                color_scheme_seed=config.color_scheme,
                font_family="Montserrat-Medium"
            )

        page.update()

    def on_settings_dropdown_changed(e: ft.ControlEvent):
        if e.control.data == "background_image_fit":
            main_container.image.fit = e.data
            config.background_image_fit = e.data
        page.update()

    def on_settings_slider_change_end(e: ft.ControlEvent):
        if e.control.data[1] == "background_image_opacity":
            main_container.image.opacity = zero_division(e.control.value, 100)
            config.background_image_opacity = int(e.control.value)
            main_container.update()
        elif e.control.data[1] == "notification_volume":
            audio.volume = zero_division(e.control.value, 100)
            config.notification_sound_volume = int(e.control.value)
            audio.update()

    def settings_sound_play(e: ft.ControlEvent):
        audio.play()

    src.tracker_analytics.arrow_left.on_click = tracker_watcher.move_left
    src.tracker_analytics.arrow_right.on_click = tracker_watcher.move_right

    src.settings.background_image.on_submit = on_settings_text_field_submit
    src.settings.notification_sound.on_submit = on_settings_text_field_submit
    src.settings.theme_color_scheme.on_submit = on_settings_text_field_submit

    src.settings.background_image_fit.on_change = on_settings_dropdown_changed

    src.settings.background_image_opacity.on_change_end = on_settings_slider_change_end
    src.settings.notification_volume.on_change_end = on_settings_slider_change_end

    src.settings.background_image.value = config.background_image_path
    src.settings.background_image_fit.value = config.background_image_fit
    src.settings.background_image_opacity.value = config.background_image_opacity
    src.settings.background_image_opacity_text.value = src.settings.background_image_opacity_text.data.format(
        str(int(config.background_image_opacity))
    )

    src.settings.notification_sound.value = config.notification_sound_path
    src.settings.notification_volume.value = config.notification_sound_volume
    src.settings.notification_volume_text.value = src.settings.notification_volume_text.data.format(
        str(int(config.notification_sound_volume))
    )
    src.tracker_analytics.activity_summary_type.on_change = lambda e: tracker_watcher.update_global_stats()

    src.settings.theme_color_scheme.value = config.color_scheme

    src.settings.notification_test_play.on_click = settings_sound_play

    src.settings.background_image_picker.on_click = lambda e: easy_picker(
        "background_image",
        "Pick a new background image",
        ft.FilePickerFileType.IMAGE,
        False
    )

    src.settings.notification_sound_picker.on_click = lambda e: easy_picker(
        "notification_sound",
        "Pick a new notification sound",
        ft.FilePickerFileType.AUDIO,
        False
    )

    # --=========== OTHER ===========-- #

    pick_files_dialog.on_result = easy_picker_result

    page.overlay.append(audio)
    page.add(main_container)

    page.run_thread(changer, os.path.abspath("assets/icon.ico"), page.title)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
    config.save()
    tracker.save()
