"""Scripts to extract the optatives of each course"""
import logging
from typing import Dict, Tuple, List

import requests
from loguru import logger
from bs4 import BeautifulSoup

from .config import settings
from .auth_handler import fetch_cookies


def scrap_optatives() -> List[Dict]:
    """Scrap all optatives for all courses and group as JSON"""
    cookie_header = fetch_cookies('https://sisacad.inf.ufsc.br/login.php')

    output: List[Dict] = []

    for course_name, course_code in crawl_course_codes(cookie_header):
        for version_name, version_code in crawl_course_versions(course_code, cookie_header):
            optatives = scrap_optatives_for_course(
                course_code, version_code, cookie_header)

            output.append({
                'course_name':  course_name,
                'course_code': course_code,
                'version_code': version_code,
                'version_name': version_name,
                'optatives': [
                    {
                        'class_code': op[0],
                        'class_name': op[1]
                    } for op in optatives
                ]
            })

    return output


def scrap_optatives_for_course(course_code: str, version: str,
                               cookie_header: Dict) -> List[Tuple[str, str]]:
    """For a couse code, extract all optatives available

    Args:
        course_code (str): course code to be sent in post request
        version (str): course version to be sent in post request
        cookie_header (Dict[str, str]): the cookie header to be sent

    Returns:
        List[Tuple[str, str]]: List of (class code, class name)
    """
    page = fetch_page(settings.teach_plans_url, 'post',
                      headers=cookie_header,
                      data={'codigo_curso': course_code,
                            'versao_id': version})

    table = page.find('table')

    if table is None:
        logger.warning('Failed to found table inside course page')
        return []

    optatives: List[Tuple[str, str]] = []
    found_header = False
    for row in table.find_all('tr'):
        if 'optativas' in row.text.lower():
            found_header = True
            continue

        if not found_header:
            continue

        try:
            td = row.find_all('td')[2]
            code, name = td.text.split(' - ', 1)
            optatives.append((code, name))

        except (ValueError, IndexError):
            logger.warning(f'Invalid row content: {row.text}')

    return optatives


def crawl_course_versions(course_code: str, cookie_header: Dict) -> List[Tuple[str, str]]:
    """Fetch options for course versions to be crawled

    Args:
        version (str): course version to be sent in post request
        cookie_header (Dict[str, str]): the cookie header to be sent

    Returns:
        List[Tuple[str, str]]: List of (version_name, version_code)
    """
    page = fetch_page(settings.teach_plans_url, 'post',
                      headers=cookie_header,
                      data={'codigo_curso': course_code})

    version_select = page.find_all('select')[1]

    ret = [(opt.text, opt.attrs['value'])
           for opt in version_select.find_all('option')
           if opt.attrs['value']]

    logger.info(f'Found versions `{ret}` for course code {course_code}')

    return ret


def crawl_course_codes(cookie_header: Dict[str, str]
                       ) -> List[Tuple[str, str]]:
    """Get links for the classes of a course pages

    Args:
        cookie_header (Dict[str, str]): the cookie header to be sent

    Returns:
        List[Tuple[str, str]]: course name and its code
    """
    page = fetch_page(settings.teach_plans_url, 'get', headers=cookie_header)

    options = page.find('select').findAll('option')

    ret = [
        (o.text, o.attrs['value'])
        for o in options
        if o.attrs['value']
    ]

    logger.info(f'Found `{len(ret)}` course codes')

    return ret


def fetch_page(url, method, **kwargs) -> BeautifulSoup:
    """Execute request for page and return as soup"""
    ret = requests.request(method, url, **kwargs)

    if ret.status_code != 200:
        raise Exception(f"Page {url} returned {ret.status_code}")

    return BeautifulSoup(ret.text, features='lxml')
