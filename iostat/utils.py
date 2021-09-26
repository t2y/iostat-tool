import logging
import os
import re
from datetime import datetime

from .consts import PACKAGE_NAME


def get_logger():
    return logging.getLogger(PACKAGE_NAME)


def parse_datetime(s, fmt='%Y%m%d%H%M%S'):
    """
    >>> parse_datetime('20170403153428')
    datetime.datetime(2017, 4, 3, 15, 34, 28)

    >>> parse_datetime('2017-04-03T15:34:28', fmt='%Y-%m-%dT%H:%M:%S')
    datetime.datetime(2017, 4, 3, 15, 34, 28)

    >>> parse_datetime('06/13/2018 02:10:50 PM', fmt='%m/%d/%Y %I:%M:%S %p')
    datetime.datetime(2018, 6, 13, 14, 10, 50)

    >>> parse_datetime('09/26/21 03:35:19', fmt='%m/%d/%y %I:%M:%S')
    datetime.datetime(2021, 9, 26, 3, 35, 19)
    """
    return datetime.strptime(s, fmt)


IOSTAT_DATE_FORMAT_EN = '%m/%d/%Y %I:%M:%S %p'
IOSTAT_DATE_EN = re.compile(r"""
(?P<date>^\d{2}/\d{2}/\d{4}\s*\d{2}:\d{2}:\d{2}\s*(AM|PM))
""", re.VERBOSE)

IOSTAT_DATE_FORMAT_JA = '%m/%d/%y %I:%M:%S'
IOSTAT_DATE_JA = re.compile(r"""
(?P<date>^\d{2}/\d{2}/\d{2}\s*\d{2}:\d{2}:\d{2})
""", re.VERBOSE)


def get_iostat_date_format(s):
    """
    >>> get_iostat_date_format('06/13/2018 02:10:50 PM')
    '%m/%d/%Y %I:%M:%S %p'
    >>> get_iostat_date_format('09/26/21 03:35:19')
    '%m/%d/%y %I:%M:%S'
    >>> get_iostat_date_format('09/26/2021 03:35:19') is None
    True
    """
    en = re.search(IOSTAT_DATE_EN, s)
    if en is not None:
        return IOSTAT_DATE_FORMAT_EN
    ja = re.search(IOSTAT_DATE_JA, s)
    if ja is not None:
        return IOSTAT_DATE_FORMAT_JA
    return None


def add_suffix_to_name(path, suffix):
    """
    >>> add_suffix_to_name('sample.log', 'test')
    'sample_test.log'
    >>> add_suffix_to_name('/path/to/name', 'test')
    '/path/to/name_test'
    >>> add_suffix_to_name('/path/to/sample.log', 'test')
    '/path/to/sample_test.log'
    """
    basename = os.path.basename(path)
    names = basename.split('.')
    names[0] = '%s_%s' % (names[0], suffix)
    name = '.'.join(names)
    return os.path.join(os.path.dirname(path), name)


def make_output_file(path, ext):
    """
    >>> make_output_file('path/to/sample.data', 'csv')
    'sample.csv'
    >>> make_output_file('path/to/sample', 'png')
    'sample.png'
    >>> make_output_file('sample.data', 'png')
    'sample.png'
    """
    filename = os.path.basename(path)
    names = filename.split('.')
    if len(names) > 0:
        name = names[0]
    return '%s.%s' % (name, ext)
