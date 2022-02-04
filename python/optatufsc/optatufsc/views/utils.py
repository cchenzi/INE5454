import pandas as pd
from typing import List
from datetime import datetime, timedelta


def _parse_schedules(schedules: str) -> str:
    if pd.isnull(schedules):
        return ""

    parsed = ""
    rows = schedules.split("\n")
    for row in rows:
        time_code, _ = row.split("/")
        time_code = time_code.strip()

        day, time = time_code.split(".")
        week_day = _parse_weekday(day)
        formated_time = _parse_time(time)

        parsed += f"{week_day}, {formated_time}\n"

    return parsed


def _parse_weekday(day: str) -> str:
    map = {
        "1": "Domingo",
        "2": "Segunda-Feira",
        "3": "Terça-Feira",
        "4": "Quarta-Feira",
        "5": "Quinta-Feira",
        "6": "Sexta-Feira",
        "7": "Sábado",
    }

    return map[day]


def _parse_time(time: str) -> str:
    start, cnt = time.split("-")

    start = datetime.strptime(start, "%H%M")

    end = start + timedelta(minutes=50 * int(cnt))
    end = _proc_intervals(start, end)

    return f"{start.strftime('%H:%M')} até {end.strftime('%H:%M')}"


def _proc_intervals(start: datetime, end: datetime) -> datetime:
    """Add time for the intervals, if necessary"""
    morning_minutes = 10
    afternoon_minutes = 20
    night_minutes = 10

    morning_interval_time = datetime.strptime("10:10", "%H:%M")
    afternoon_interval_time = datetime.strptime("16:00", "%H:%M")
    night_interval_time = datetime.strptime("20:10", "%H:%M")

    if start < morning_interval_time < end:
        end += timedelta(minutes=morning_minutes)

    elif start < afternoon_interval_time < end:
        end += timedelta(minutes=afternoon_minutes)

    elif start < night_interval_time < end:
        end += timedelta(minutes=night_minutes)

    return end


def fix_professors_columns(data: pd.DataFrame) -> pd.DataFrame:
    data["professors_list"] = (
        data["professors"]
        .fillna("")
        .str.split("\n")
        .apply(lambda prof_list: [prof.strip() for prof in prof_list])
    )
    data["professors"] = data["professors_list"].apply(
        lambda prof_list: ",\n".join(prof_list)
    )
    return data
