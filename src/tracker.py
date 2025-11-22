import json
import os

from enum import Enum
from dataclasses import dataclass, asdict, field

from src.shared import get_user_data_filepath, get_today, get_time


class DataType(Enum):
    focus = "focus"
    short_break = "short_break"
    long_break = "long_break"
    pause = "pause"
    short_task = "short_task"


@dataclass
class Tracker:
    data: dict = field(default_factory=dict)
    config_path: str = field(
        default="",
        init=False,
        repr=False,
        compare=False
    )

    def __post_init__(self):
        self.tracking_data_path = get_user_data_filepath("tracking_data.json")

    @staticmethod
    def normalize_type(value: str | DataType) -> DataType:
        if isinstance(value, DataType):
            return value
        return DataType(value)

    def add(self, data_type: DataType | str, *args):
        data_type = self.normalize_type(data_type)

        today = get_today()
        if self.data.get(today) is None:
            self.data[today] = {}

        if self.data[today].get(args[0]) is None:
            self.data[today][args[0]] = {}

        if data_type != DataType.pause and data_type != DataType.short_task:
            self.data[today][args[0]]["type"] = data_type.value
            self.data[today][args[0]]["end_time"] = get_time()
        elif data_type == DataType.short_task:
            self.data[today][args[0]]["short_task"] = args[1]
        else:
            if self.data[today][args[0]].get("pauses") is None:
                self.data[today][args[0]]["pauses"] = [
                    [args[1], args[2]]
                ]
            else:
                self.data[today][args[0]]["pauses"].append([
                    args[1],
                    args[2]
                ])

    def save(self):
        self._create_json_file()

    def load(self):
        if not os.path.exists(self.tracking_data_path):
            self._create_json_file()
        with open(self.tracking_data_path, "r", encoding="utf-8") as s_file:
            for key, value in json.load(s_file).items():
                setattr(self, key, value)

    def _create_json_file(self):
        with open(self.tracking_data_path, "w", encoding="utf-8") as c_file:
            json.dump(asdict(self), c_file)
