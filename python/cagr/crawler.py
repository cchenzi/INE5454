"""Crawl functions"""
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        self.CAGR_URL = "https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/"

        self.setup_campi_and_semesters()

    def setup_campi_and_semesters(self):
        """Get the class registry page and extract available semesters and campi"""
        soup = BeautifulSoup(requests.get(self.CAGR_URL).content)
        # TODO handle connection errors

        self.av_semesters: List[str] = [
            option.text
            for option in (
                soup
                .find('select', {'id': 'formBusca:selectSemestre'})
                .findAll('option'))
        ]

        self.campi: List[str] = [
            option.text
            for option in (
                soup
                .find('select', {'id': 'formBusca:selectCampus'})
                .findAll('option'))
        ]

    def form(self, semester: str, course_code: str, campus: str) -> Dict:
        return {
            'formBusca:selectSemetre': semester,
            'formBusca:selectCursosGraduacao': course_code,
            'formBusca:selectCampus': campus
        }

    def crawl_course(self, course_code: str, limit_semesters: int) -> List[Dict]:
        """For a course code, crawl up to limit_semesters (most recent ordered) classes"""
        semesters_to_crawl = self.av_semesters[:limit_semesters]

        # CONTINUE HERE
