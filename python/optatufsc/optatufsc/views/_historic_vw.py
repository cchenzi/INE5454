"""View to analyse frequency of the courses availability"""
from typing import List
from datetime import datetime, timedelta

from .utils import _parse_schedules, _parse_weekday, _parse_time, _proc_intervals

import pandas as pd
import streamlit as st


def historic_vw(data_source: pd.DataFrame):
    courses = _get_available_courses(data_source)
    selected_course = st.selectbox("Curso", courses)

    class_filter_map = {
        "Nome": lambda k: k[2],
        "Código": lambda k: k[1],
        "Professor": lambda k: k[3],
    }

    left, right = st.columns((1, 4))

    with left:
        selected_class_filter = st.selectbox("Filtrar por", class_filter_map.keys())

    with right:
        classes = _get_available_classes(data_source, selected_course)
        if selected_class_filter != "Professor":
            selected_class_code = st.selectbox(
                "Matéria",
                classes.itertuples(),
                format_func=class_filter_map[selected_class_filter],
            )[1]
            filtered_data = _filter_by_class_code(data_source, selected_class_code)
        else:
            professors = _get_professors(data_source, selected_course)
            selected_professor_name = st.selectbox(
                "Nome",
                professors,
            )
            filtered_data = _filter_by_professor(data_source, selected_professor_name)

    formatted_data = _format_data(filtered_data, selected_class_filter)

    styler = formatted_data.style
    styler.hide(axis="index")

    st.write(styler.to_html(), unsafe_allow_html=True)


def _get_available_courses(data: pd.DataFrame) -> List[str]:
    return list(data["course_name"].unique())


def _get_available_classes(data: pd.DataFrame, course: str) -> pd.DataFrame:
    return data[data["course_name"] == course][
        ["class_code", "class_name"]
    ].drop_duplicates()


def _get_professors(data: pd.DataFrame) -> List[str]:
    return data.explode("professors")["professors"].unique()


def _get_professors(data: pd.DataFrame, course: str) -> List[str]:
    data = data[data["course_name"] == course][["professors_list"]].explode(
        "professors_list"
    )
    return sorted(list(data["professors_list"].dropna().unique()))


def _filter_by_class_code(data: pd.DataFrame, class_code: str) -> pd.DataFrame:
    return data[data["class_code"] == class_code]


def _filter_by_professor(data: pd.DataFrame, professor_name: str) -> pd.DataFrame:
    data = data.explode("professors_list")
    return data[data["professors_list"] == professor_name]


def _format_data(data: pd.DataFrame, filter_key: str) -> pd.DataFrame:
    desired_columns = ["semester", "open_slots", "schedules", "professors"]
    if filter_key == "Professor":
        desired_columns.extend(["class_code", "class_name"])
    data = data[desired_columns]
    data = data.sort_values(by="semester", ascending=False)
    data["schedules"] = data["schedules"].apply(_parse_schedules)

    data = data.drop_duplicates()
    data = data.rename(
        columns={
            "semester": "Semestre",
            "open_slots": "Vagas",
            "schedules": "Horários",
            "professors": "Professores",
            "class_code": "Cód.",
            "class_name": "Matéria",
        }
    )

    return data
