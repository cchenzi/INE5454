"""Render view to show some graphs and stats"""
from datetime import timedelta, datetime
from typing import List, Tuple, Dict

from .utils import _parse_schedules, _parse_weekday, _parse_time, _proc_intervals

import streamlit as st
import pandas as pd


def stats_view(data: pd.DataFrame):
    left, right = st.columns(2)

    
    data = data.head(10)
    styler = data.style
    styler.hide(axis="index")

    st.write(styler.to_html(), unsafe_allow_html=True)