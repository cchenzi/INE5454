"""Render view to filter and search for classes"""
from datetime import timedelta, datetime
from typing import List, Tuple, Dict

from .utils import _parse_schedules, _parse_weekday, _parse_time, _proc_intervals

import streamlit as st
import pandas as pd


def optatives_view(data: pd.DataFrame):
    left, right = st.columns(2)

    campi = _get_available_campi(data)
    with left:
        campus = st.selectbox(label="Campus", options=campi)

    semesters = _get_available_semesters(data)
    with right:
        semester = st.selectbox(label="Semestre", options=semesters)

    courses = _get_available_courses(data, semester)
    course = st.selectbox(label="Curso", options=courses, format_func=lambda k: k[1])

    df = _get_available_optatives(data, semester, course[0], campus)
    df = _format_data(df)
    styler = df.style
    styler.hide(axis="index")

    st.write(styler.to_html(), unsafe_allow_html=True)


def _get_available_semesters(data: pd.DataFrame) -> List[str]:
    semesters = list(data["semester"].unique())
    semesters.sort(reverse=True)

    return semesters


def _get_available_campi(data: pd.DataFrame()) -> List[str]:
    campi = list(data["campus"].unique())
    campi.sort()
    campi = ["Todos", *campi]

    return campi


def _get_available_courses(data: Dict, semester: str) -> [Tuple[str, str]]:
    semester_filtered = data[data["semester"] == semester]
    all_courses = semester_filtered[["course_code", "course_name"]].drop_duplicates()
    courses = [(d["course_code"], d["course_name"]) for _, d in all_courses.iterrows()]

    courses.sort(key=lambda k: k[1])
    courses = [("Todos", "Todos"), *courses]

    return courses


def _get_available_optatives(
    data: Dict, semester: str, course_code: str, campus: str
) -> pd.DataFrame:
    rows = data[(data["semester"] == semester)]

    if campus != "Todos":
        rows = rows[rows["campus"] == campus]

    if course_code != "Todos":
        rows = rows[rows["course_code"] == course_code]

    return rows[
        [
            "class_code",
            "class_name",
            "class",
            "professors",
            "schedules",
            "open_slots",
            "total_hours",
        ]
    ]


def _format_data(df: pd.DataFrame) -> pd.DataFrame:
    df["schedules"] = df["schedules"].apply(_parse_schedules)
    df = df.rename(
        columns={
            "class_code": "Cod.",
            "class_name": "Nome",
            "class": "Turma",
            "professors": "Professores",
            "schedules": "Horários",
            "open_slots": "Vagas",
            "total_hours": "H/a",
        }
    )

    # Re order
    df = df[["Turma", "Cod.", "Nome", "Horários", "Vagas", "H/a", "Professores"]]

    return df
