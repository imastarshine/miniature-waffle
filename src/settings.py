import flet as ft


def on_slider_change(e: ft.ControlEvent):
    value = e.control.value
    slider_text = e.control.data[0]

    slider_text.value = slider_text.data.format(str(int(value)))
    slider_text.update()


def file_picker_button() -> ft.TextButton:
    return ft.TextButton(
        text="Select a file",
        icon=ft.Icons.ATTACH_FILE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )


def generate_slider_column(slider: ft.Slider, slider_text: ft.Text) -> ft.Column:
    return ft.Column(
        [
            slider_text,
            slider
        ],
        spacing=2,
        alignment=ft.MainAxisAlignment.END,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


background_image = ft.TextField(
    content_padding=ft.padding.symmetric(12, 12),
    border=ft.InputBorder.OUTLINE,
    height=48,
    border_radius=ft.border_radius.all(10),
    border_width=2,
    border_color=ft.Colors.SECONDARY_CONTAINER,
    focused_border_color=ft.Colors.PRIMARY,
    hint_text="Background image path (URL/File)",
    text_align=ft.TextAlign.CENTER,
    data="background_image"
)

background_image_fit = ft.Dropdown(
    value="fitHeight",
    options=[
        ft.DropdownOption(key=item.value, content=ft.Text(item.value.capitalize())) for item in ft.ImageFit
    ],
    border_color=ft.Colors.SECONDARY_CONTAINER,
    border_width=2,
    border_radius=10,
    data="background_image_fit"
)

background_image_opacity_text = ft.Text(
    value="Opacity: 20%",
    data="Opacity: {}%"
)

background_image_opacity = ft.Slider(
    value=20,
    min=0,
    max=100,
    on_change=on_slider_change,
    data=(background_image_opacity_text, "background_image_opacity"),
    padding=ft.Padding(24, 0, 24, 0)
)

background_image_picker = file_picker_button()

notification_sound = ft.TextField(
    content_padding=ft.padding.symmetric(12, 12),
    border=ft.InputBorder.OUTLINE,
    height=48,
    border_radius=ft.border_radius.all(10),
    border_width=2,
    border_color=ft.Colors.SECONDARY_CONTAINER,
    focused_border_color=ft.Colors.PRIMARY,
    hint_text="Notification sound (URL/File)",
    text_align=ft.TextAlign.CENTER,
    data="notification_sound"
)

notification_sound_picker = file_picker_button()

notification_volume_text = ft.Text(
    value="Volume: 50%",
    data="Volume: {}%"
)

notification_volume = ft.Slider(
    value=50,
    min=0,
    max=100,
    on_change=on_slider_change,
    data=(notification_volume_text, "notification_volume"),
    padding=ft.Padding(24, 0, 24, 0)
)

notification_test_play = ft.TextButton(
    text="Play",
    icon=ft.Icons.PLAY_ARROW,
    style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10)
    )
)

theme_color_scheme = ft.TextField(
    content_padding=ft.padding.symmetric(12, 12),
    border=ft.InputBorder.OUTLINE,
    height=48,
    border_radius=ft.border_radius.all(10),
    border_width=2,
    border_color=ft.Colors.SECONDARY_CONTAINER,
    focused_border_color=ft.Colors.PRIMARY,
    hint_text="Theme color scheme (Green / #000000)",
    text_align=ft.TextAlign.CENTER,
    expand=True,
    data="theme_color_scheme"
)


alert_dialog = ft.AlertDialog(
    title="Settings",
    content=ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Divider(
                        opacity=0,
                        height=0
                    ),
                    ft.Text("Background image"),
                    background_image,
                    background_image_picker,
                    ft.Row(
                        [
                            ft.Text(
                                "Fit",
                                text_align=ft.TextAlign.RIGHT,
                                expand=True,
                                size=18
                            ),
                            background_image_fit
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    generate_slider_column(
                        background_image_opacity,
                        background_image_opacity_text
                    ),
                    ft.Divider(),
                    ft.Text("Sound"),
                    notification_sound,
                    notification_sound_picker,
                    generate_slider_column(
                        notification_volume,
                        notification_volume_text
                    ),
                    notification_test_play,
                    ft.Divider(),
                    ft.Text("Theme"),
                    theme_color_scheme,
                    ft.Divider(
                        opacity=0,
                        height=0
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
                expand=True
            ),
            padding=ft.padding.only(8, 0, 8, 0),
            expand=True
        ),
        expand=True
    ),
    actions_padding=0,
    content_padding=ft.padding.only(10, 0, 10, 10),
    title_padding=ft.padding.only(20, 16, 20, 8),
    alignment=ft.alignment.center
)
