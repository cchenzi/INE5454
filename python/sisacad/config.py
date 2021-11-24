"""Centralized setup"""
import os
from typing import NamedTuple


class Settings(NamedTuple):
    # Need to be formatted in runtime
    auth_url: str = 'https://sistemas.ufsc.br/login?service={}'

    auth_username: str = os.environ['USERNAME']
    auth_password: str = os.environ['PASSWORD']

    teach_plans_url: str = 'https://sisacad.inf.ufsc.br/modules/user/index.php?item=programas_ensino&topico=curso'


settings = Settings()
