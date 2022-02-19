import os

import streamlit as st
import pandas as pd

from views import optatives_vw, historic_vw
from views.utils import fix_professors_columns

DATA_SOURCE = os.path.join(os.path.dirname(__file__), "../../../data/optatufsc.csv")

logo = '<img src="https://i.imgur.com/qP38IBM.png" alt="Universidade Federal de Santa Catarina" style="border:0px;margin-left:20px;margin-top:7px;float:right;  width:90px;"></img>'
logo_html = '<div style="text-align: right;">' + logo + "</div>"


def main():
    setup_page()

    tabs_map = {
        "Matérias optativas": optatives_vw,
        "Históricos de disponibilização": historic_vw,
    }

    select_tab = st.sidebar.selectbox("Aba", tabs_map.keys())

    data = pd.read_csv(DATA_SOURCE, dtype=str)
    data = fix_professors_columns(data)

    tabs_map[select_tab](data)


def setup_page():
    st.set_page_config(layout="wide")
    st.markdown(
        logo_html,
        unsafe_allow_html=True,
    )
    st.title("optatUFSC")


if __name__ == "__main__":
    main()
