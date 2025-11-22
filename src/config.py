import json
import os
from dataclasses import dataclass, asdict, field

from src.shared import get_user_data_filepath


@dataclass
class Config:
    color_scheme: str = "cyan"
    theme_mode: str = "system"

    background_image_path: str = ""
    background_image_fit: str = "fitHeight"
    background_image_opacity: float = 20

    notification_sound_path = "assets/sounds/success.mp3"
    notification_sound_volume: float = 40

    pomodoro_time: int = 1500
    short_break_time: int = 300
    long_break_time: int = 900

    config_path: str = field(
        default="",
        init=False,
        repr=False,
        compare=False
    )

    def __post_init__(self):
        self.config_path = get_user_data_filepath("config.json")

    def save(self):
        self._create_json_file()

    def load(self):
        if not os.path.exists(self.config_path):
            self._create_json_file()
        with open(self.config_path, "r") as s_file:
            for key, value in json.load(s_file).items():
                setattr(self, key, value)

    def _create_json_file(self):
        with open(self.config_path, "w") as c_file:
            json.dump(asdict(self), c_file)
