import os

from .filters import get_filters
from .utils import get_iostat_date_format
from .utils import get_logger
from .utils import parse_datetime

log = get_logger()


class Parser:

    CPU = 'CPU'
    DATE = 'DATE'
    DEVICE = 'Device'

    def __init__(self, args):
        self.args = args
        self.extra_lines = []
        self.state = None
        self.filters = get_filters(args)
        self.init_stat()

    def init_stat(self):
        self.date = None
        self.cpu_stat = {'columns': None, 'stat': None}
        self.device_stat = {'columns': None, 'stats': []}

    def make_stat(self):
        stat = {
            'date': self.date,
            'cpu': self.cpu_stat,
            'device': self.device_stat,
        }
        self.init_stat()
        return stat

    def parse_cpu_stat(self, line):
        self.cpu_stat['stat'] = [float(i) for i in line.split()]

    def parse_device_stat(self, line):
        s = line.split()
        stat = {s[0]: [float(i) for i in s[1:]]}
        self.device_stat['stats'].append(stat)

    def parse_columns(self, d, line):
        d['columns'] = line.strip().split()[1:]

    def _parse(self, line):
        if line == '\n':
            self.state = None
            return

        line = line.strip()
        if self.state == self.CPU:
            self.parse_cpu_stat(line)
        elif self.state == self.DEVICE:
            self.parse_device_stat(line)
        else:
            date_format = get_iostat_date_format(line)
            if date_format is not None:
                if self.date is not None:
                    yield self.make_stat()

                self.init_stat()
                self.date = parse_datetime(line, fmt=date_format)
                self.state = self.DATE
            else:
                if line.startswith('avg-cpu:'):
                    self.parse_columns(self.cpu_stat, line)
                    self.state = self.CPU
                elif line.startswith('Device'):
                    self.parse_columns(self.device_stat, line)
                    self.state = self.DEVICE
                else:
                    log.debug('not handled line: %s', line)
                    self.extra_lines.append(line)

    def parse_line(self, line):
        yield from self._parse(line)

    def parse_all(self):
        if not os.path.isfile(self.args.data):
            log.error('target file is not found: %s', self.args.data)
            return

        with open(self.args.data) as f:
            for line in f:
                yield from self._parse(line)
            yield self.make_stat()  # last stat data

    def filter(self, stat):
        for filter_func in self.filters:
            if not filter_func(stat):
                return False
        return True

    def parse(self):
        for stat in self.parse_all():
            if self.filter(stat):
                yield stat
