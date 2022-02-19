import os

import streamlit as st
import pandas as pd

from views import optatives_view, historic_view, stats_view
from views.utils import fix_professors_columns

DATA_SOURCE = os.path.join(
    os.path.dirname(__file__), "../../../data/optatufsc.csv"
)


def main():
    setup_page()

    tabs_map = {
        "Matérias optativas": optatives_view,
        "Históricos de disponibilização": historic_view,
        "Estatísticas e gráficos": stats_view
    }

    select_tab = st.sidebar.selectbox("Aba", tabs_map.keys())

    data = pd.read_csv(DATA_SOURCE, dtype=str)
    data = fix_professors_columns(data)

    tabs_map[select_tab](data)


def setup_page():
    st.set_page_config(layout="wide")


if __name__ == "__main__":
    main()
