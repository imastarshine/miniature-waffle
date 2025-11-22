import os
from datetime import datetime


def get_user_data_filepath(filename: str) -> str:
    data_dir = os.getenv("FLET_APP_STORAGE_DATA")
    if data_dir is None:
        data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename)


def get_today() -> str:
    now_aware = datetime.now().astimezone()
    start_of_day = now_aware.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_of_day.isoformat()


def get_today_dt() -> str:
    now_aware = datetime.now().astimezone()
    start_of_day = now_aware.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_of_day


def get_time() -> str:
    now_naive = datetime.now()
    time_aware = now_naive.astimezone()
    return time_aware.isoformat()


def get_time_dt() -> str:
    now_naive = datetime.now()
    time_aware = now_naive.astimezone()
    return time_aware.isoformat()
