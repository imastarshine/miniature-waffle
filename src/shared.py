from datetime import datetime


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
