import flet as ft
from datetime import datetime, timedelta


def _column_title(text0: ft.Text, text1: ft.Text):
    return ft.Column(
        [
            text0,
            text1
        ],
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )


def _space():
    return ft.Divider(
        opacity=0,
        height=7
    )


def _space_7():
    return ft.Divider(
        opacity=0,
        height=6
    )


class TrackerWatcher:

    def __init__(self, page: ft.Page, session_tracker_data: dict):
        self.page = page
        self.session_tracker_data = session_tracker_data
        self.selected_day_str = ""
        self.selected_day_index = 0
        self._cl_session_tracker_data = []  # cl means cached list

    @staticmethod
    def create_session_container(
            start_dt: datetime,
            end_dt: datetime,
            session_id: int,
            session_type: str,
            pauses: dict,
            short_task: str | None
    ):
        icon = ft.Icon(ft.Icons.TIMER) if session_type == "focus" else ft.Icon(ft.Icons.PLAY_ARROW)

        total_duration = end_dt.timestamp() - start_dt.timestamp()

        hours = int(total_duration // 3600)
        minutes = int((total_duration % 3600) // 60)
        duration_text = f"{hours}h {minutes}m"

        total_pause_duration = timedelta(0)
        for pause in pauses:
            if len(pause) == 2:
                pause_start = datetime.fromisoformat(pause[0])
                pause_end = datetime.fromisoformat(pause[1])
                total_pause_duration += (pause_end - pause_start)

        total_pauses = len(pauses)
        pause_hours = int(total_pause_duration.total_seconds() // 3600)
        pause_minutes = int((total_pause_duration.total_seconds() % 3600) // 60)
        pause_duration_text = f"{pause_hours}h {pause_minutes}m"

        header_row = ft.Row(
            [
                icon,
                ft.Text(f"Session {session_id} — {session_type.capitalize()}"),
                ft.Text(duration_text, text_align=ft.TextAlign.RIGHT, expand=True, weight=ft.FontWeight.BOLD)
            ],
            spacing=8
        )

        total_pauses_bool = total_pauses > 0
        short_task_bool = short_task is not None
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=13, opacity=0.8, color=ft.Colors.ON_SURFACE),
                        ft.Container(width=2),
                        ft.Text(
                            start_dt.strftime("%H:%M"), size=13, opacity=0.8
                        ),
                        ft.Icon(ft.Icons.ARROW_RIGHT, size=16, opacity=0.8, color=ft.Colors.ON_SURFACE),
                        ft.Text(
                            end_dt.strftime("%H:%M"), size=13, opacity=0.8
                        )
                    ],
                    spacing=2
                ),
                header_row
            ],
            spacing=4
        )

        if total_pauses_bool:
            pause_row = ft.Row(
                [
                    ft.Container(width=21),
                    ft.Icon(ft.Icons.PAUSE, size=13),
                    ft.Text(f"{total_pauses} Pause{'s' if total_pauses > 1 else ''}", size=13),
                    ft.Text(
                        pause_duration_text,
                        text_align=ft.TextAlign.RIGHT,
                        expand=True,
                        size=13,
                        weight=ft.FontWeight.W_200
                    )
                ],
                spacing=6
            )
            content.controls.append(pause_row)
        if short_task_bool and short_task != "":
            short_task_row = ft.Row(
                [
                    ft.Container(width=21),
                    ft.Icon(ft.Icons.EDIT, size=13),
                    ft.Text(short_task, size=13)
                ],
                spacing=6
            )
            content.controls.append(short_task_row)

        if len(session_column.controls) > 0:
            session_column.controls.append(ft.Divider())
        session_column.controls.append(ft.Container(content=content))

    @staticmethod
    def clean_session_container():
        session_column.controls.clear()

    def get_day_by_index(self, index: int):
        try:
            if index < len(self._cl_session_tracker_data):
                return self._cl_session_tracker_data[index]
            else:
                return None
        except IndexError:
            return None

    def try_move_left(self, override: bool = False):
        current_index = self.get_day_by_index(self.selected_day_index - 1)
        if current_index is not None:
            if override is True:
                self.selected_day_index = self.selected_day_index - 1
                self.selected_day_str = current_index
            arrow_left.disabled = False
        else:
            arrow_left.disabled = True
        arrow_left.update()

    def try_move_right(self, override: bool = False):
        current_index = self.get_day_by_index(self.selected_day_index + 1)
        if current_index is not None:
            if override is True:
                self.selected_day_index = self.selected_day_index + 1
                self.selected_day_str = current_index
            arrow_right.disabled = False
        else:
            arrow_right.disabled = True
        arrow_right.update()

    def on_open(self, tracker_data: dict):
        self.session_tracker_data = tracker_data
        self._cl_session_tracker_data = list(self.session_tracker_data.keys())
        if self.selected_day_str == "":
            self.selected_day_str = self._cl_session_tracker_data[-1]
            self.selected_day_index = len(self._cl_session_tracker_data) - 1

        self.page.open(alert_dialog)
        self.update_global_stats()
        self.day_stats_update()

    def update_global_stats(self):
        now = datetime.now()
        now_timestamp = now.timestamp()

        # Calculate total time spent
        total_time = 0
        focus_time_total = 0
        chill_time_total = 0

        for day_session_iso, data in self.session_tracker_data.items():
            day_session_dt = datetime.fromisoformat(day_session_iso)
            day_session_timestamp = day_session_dt.timestamp()

            if activity_summary_type.value == "Month":
                if day_session_timestamp < (now_timestamp - 30 * 24 * 60 * 60):
                    continue
            elif activity_summary_type.value == "Week":
                if day_session_timestamp < (now_timestamp - 7 * 24 * 60 * 60):
                    continue
            elif activity_summary_type.value == "Day":
                if day_session_timestamp < (now_timestamp - 24 * 60 * 60):
                    continue

            for session_iso, session_data in data.items():
                session_start = datetime.fromisoformat(session_iso)
                end_time = datetime.fromisoformat(session_data.get("end_time"))
                session_type = session_data.get("type")

                pauses = session_data.get("pauses", [])
                pause_time = 0
                for pause in pauses:
                    pause_start = datetime.fromisoformat(pause[0])
                    pause_end = datetime.fromisoformat(pause[1])
                    pause_time += pause_end.timestamp() - pause_start.timestamp()

                if session_type == "focus":
                    focus_time_total += end_time.timestamp() - session_start.timestamp() - pause_time
                else:
                    chill_time_total += end_time.timestamp() - session_start.timestamp() - pause_time

        total_time = focus_time_total + chill_time_total

        total_time_spent.value = str(timedelta(seconds=int(total_time)))
        total_focus_time.value = str(timedelta(seconds=int(focus_time_total)))
        total_chill_time.value = str(timedelta(seconds=int(chill_time_total)))

        self.page.update()

    def move_left(self, e: ft.ControlEvent):
        self.try_move_left(override=True)
        self.day_stats_update()

    def move_right(self, e: ft.ControlEvent):
        self.try_move_right(override=True)
        self.day_stats_update()

    def day_stats_update(self):
        session_data = self.session_tracker_data.get(self.selected_day_str, {})
        self.clean_session_container()
        self.page.update()

        focus_time_total = 0
        chill_time_total = 0
        total_time = 0
        session_id = 0

        # counter some stuff
        for session_iso, session_data in session_data.items():
            session_id += 1
            session_start = datetime.fromisoformat(session_iso)
            end_time = datetime.fromisoformat(session_data.get("end_time"))
            session_type: str = session_data.get("type")

            pauses = session_data.get("pauses", [])
            pause_time = 0
            for pause in pauses:
                pause_start = datetime.fromisoformat(pause[0])
                pause_end = datetime.fromisoformat(pause[1])
                pause_time += pause_end.timestamp() - pause_start.timestamp()

            if session_type == "focus":
                focus_time_total += end_time.timestamp() - session_start.timestamp() - pause_time
            else:
                chill_time_total += end_time.timestamp() - session_start.timestamp() - pause_time

            self.create_session_container(
                session_start,
                end_time,
                session_id,
                " ".join(session_type.split("_")),
                pauses,
                session_data.get("short_task", None)
            )

        current_day_dt = datetime.fromisoformat(self.selected_day_str)

        total_time = focus_time_total + chill_time_total

        total_time_day.value = str(timedelta(seconds=int(total_time)))
        total_focus_time_day.value = str(timedelta(seconds=int(focus_time_total)))
        total_chill_time_day.value = str(timedelta(seconds=int(chill_time_total)))

        current_day.value = current_day_dt.strftime("%A, %B %d, %Y")
        self.try_move_left(override=False)
        self.try_move_right(override=False)
        self.page.update()

total_time_spent = ft.Text(
    "0d 0h 0m",
    size=28,
    weight=ft.FontWeight.BOLD
)
total_focus_time = ft.Text(
    "0d 0h 0m",
    size=28,
    weight=ft.FontWeight.W_200
)
total_chill_time = ft.Text(
    "0d 0h 0m",
    size=28,
    weight=ft.FontWeight.W_200
)
analytics_button = ft.IconButton(
    icon=ft.Icons.ANALYTICS,
    style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10)
    )
)
current_day = ft.Text(
    "Today",
    size=20,
    weight=ft.FontWeight.W_400,
    text_align=ft.TextAlign.CENTER,
    expand=True
)
arrow_left = ft.IconButton(
    icon=ft.Icons.ARROW_BACK,
    style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10)
    )
)
arrow_right = ft.IconButton(
    icon=ft.Icons.ARROW_FORWARD,
    style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10)
    )
)
total_time_day = ft.Text(
    "0d 0h 0m",
    size=20,
    weight=ft.FontWeight.W_200
)
total_focus_time_day = ft.Text(
    "0d 0h 0m",
    size=20,
    weight=ft.FontWeight.W_200
)
total_chill_time_day = ft.Text(
    "0d 0h 0m",
    size=20,
    weight=ft.FontWeight.W_200,
    text_align=ft.TextAlign.CENTER
)
activity_summary_type = ft.Dropdown(
    value="All Time",
    options=[
        ft.DropdownOption(key="All Time", content=ft.Text("All Time")),
        ft.DropdownOption(key="Month", content=ft.Text("Month")),
        ft.DropdownOption(key="Week", content=ft.Text("Week")),
        ft.DropdownOption(key="Day", content=ft.Text("Day"))
    ],
    border_color=ft.Colors.SECONDARY_CONTAINER,
    border_width=2,
    border_radius=10
)
session_column = ft.Column([])

alert_dialog = ft.AlertDialog(
    title="Analytics",
    content=ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    _space(),
                    ft.Container(
                        content=ft.Text(
                            "Activity Summary",
                            size=14,
                            opacity=0.8,
                            expand=True,
                            text_align=ft.TextAlign.CENTER
                        ),
                        alignment=ft.alignment.center
                    ),
                    _space_7(),
                    ft.Row(
                        [
                            ft.Text(
                                "Date range",
                                expand=True,
                                size=16
                            ),
                            activity_summary_type
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            _column_title(
                                ft.Text("Time spent", size=16),
                                total_time_spent
                            ),
                            ft.VerticalDivider(),
                            _column_title(
                                ft.Text("Focus time", size=16),
                                total_focus_time
                            )
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        content=_column_title(
                            ft.Text("Chill time", size=16),
                            total_chill_time
                        ),
                        alignment=ft.alignment.center
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    _space_7(),
                                    ft.Row(
                                        [
                                            arrow_left,
                                            current_day,
                                            arrow_right
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        expand=True
                                    ),
                                    ft.Divider(),
                                    ft.Row(
                                        [
                                            _column_title(
                                                ft.Text("Total time", size=13, expand=True),
                                                total_time_day
                                            ),
                                            ft.VerticalDivider(),
                                            _column_title(
                                                ft.Text("Focus time", size=13, expand=True),
                                                total_focus_time_day
                                            )

                                        ],
                                        spacing=4,
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    ft.Container(
                                        content=_column_title(
                                            ft.Text("Chill time", size=13, expand=True, text_align=ft.TextAlign.CENTER),
                                            total_chill_time_day
                                        ),
                                        alignment=ft.alignment.center
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            "Sessions",
                                            size=16,
                                            expand=True,
                                            text_align=ft.TextAlign.CENTER,
                                            opacity=0.8
                                        ),
                                        alignment=ft.alignment.center
                                    ),
                                    session_column,
                                    _space_7()
                                ],
                                spacing=4,
                                expand=True
                            ),
                            padding=ft.padding.only(12, 0, 12, 0),
                            expand=True
                        ),
                        color=ft.Colors.ON_SECONDARY
                    ),
                    _space()
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=4,
                expand=True
            ),
            padding=ft.padding.only(12, 0, 12, 0),
            expand=True
        ),
        expand=True,
        shadow_color=ft.Colors.TRANSPARENT
    ),
    actions_padding=0,
    content_padding=ft.padding.only(10, 0, 10, 10),
    title_padding=ft.padding.only(20, 16, 20, 8),
    alignment=ft.alignment.center
)
