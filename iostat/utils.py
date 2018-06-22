# -*- coding: utf-8 -*-
import logging
import os
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
    """
    return datetime.strptime(s, fmt)


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
