import json
import os

from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict, field


def get_today() -> str:
    now_aware = datetime.now().astimezone()
    start_of_day = now_aware.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_of_day.isoformat()


def get_time() -> str:
    now_naive = datetime.now()
    time_aware = now_naive.astimezone()
    return time_aware.isoformat()


class DataType(Enum):
    focus = "focus"
    short_break = "short_break"
    long_break = "long_break"
    pause = "pause"
    short_task = "short_task"


@dataclass
class Tracker:
    data: dict = field(default_factory=dict)

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
        if not os.path.exists("data/tracking_data.json"):
            self._create_json_file()
        with open("data/tracking_data.json", "r", encoding="utf-8") as s_file:
            for key, value in json.load(s_file).items():
                setattr(self, key, value)

    def _create_json_file(self):
        with open("data/tracking_data.json", "w", encoding="utf-8") as c_file:
            json.dump(asdict(self), c_file)

