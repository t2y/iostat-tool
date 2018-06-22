import csv
from contextlib import ContextDecorator

from .utils import add_suffix_to_name


class BaseWriter(ContextDecorator):

    def __init__(self, args, suffix):
        self.args = args
        output = add_suffix_to_name(args.output, suffix)
        self.f = open(output, 'w')
        self.writer = csv.writer(
            self.f, dialect=args.dialect, delimiter=args.separator,
            quoting=csv.QUOTE_MINIMAL
        )

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.f.close()

    def write(self, row):
        self.writer.writerow(row)


class CPUWriter(BaseWriter):

    def __init__(self, args):
        suffix = 'cpu'
        super().__init__(args, suffix)


class DeviceWriter(BaseWriter):

    def __init__(self, args):
        suffix = 'devices'
        super().__init__(args, suffix)

    def write_rows(self, date, stats):
        for disk_stat in stats:
            for name, stat in disk_stat.items():
                row = [date, name]
                row.extend(stat)
                self.writer.writerow(row)


def write_csv(args, parser):
    def make_row(date, stat):
        row = [date]
        row.extend(stat)
        return row

    g = parser.parse()
    first_row = next(g)
    with CPUWriter(args) as cpu, DeviceWriter(args) as device:
        # write first row after csv header
        cpu.write(make_row('datetime', first_row['cpu']['columns']))
        cpu.write(make_row(first_row['date'], first_row['cpu']['stat']))
        device.write(['datetime', 'device'] + first_row['device']['columns'])
        device.write_rows(first_row['date'], first_row['device']['stats'])
        # sencod rows
        for stat in g:
            cpu.write(make_row(stat['date'], stat['cpu']['stat']))
            device.write_rows(stat['date'], stat['device']['stats'])
