import math
from collections import defaultdict

from matplotlib import dates as mdates
from matplotlib import gridspec
from matplotlib import pyplot as plt

from .consts import AVGRQ_SZ, AVGQU_SZ, AWAIT, SVCTM
from .consts import IO_RQM, IOPS, IO_TRANSFER, PERCENT_UTIL
from .consts import PERCENT_IO_RQM
from .renderer import Renderer
from .utils import get_logger

log = get_logger()
default_figsize = plt.rcParams.get('figure.figsize')


class Plotter(Renderer):

    def __init__(self, args, stats):
        self.args = args
        self.stats = stats
        self.subplot_borderaxespad = -1

        figsize = args.figsize
        if figsize is None:
            figsize = (18, 14)

        self.fig = plt.figure(figsize=figsize)
        self.fig.suptitle(self.args.title)

        if self.args.cpu_only:
            self.args.subplots = []

        if self.args.with_cpu:
            add_rows = 1
        else:
            add_rows = 0

        self._update_args_subplots()
        row_length = math.ceil(len(self.args.subplots) / 2.0)
        gs = gridspec.GridSpec(row_length + add_rows, 2, wspace=0.4)

        if args.with_cpu:
            self.cpu = self.fig.add_subplot(gs[0, :])
            self.cpu.set_title('cpu average')
            self.cpu.set_ylim(0, 100)
            self.cpu.set_ylabel('percent')

        self.subplots = {}
        gs_range = [(i, j) for j in (0, 1)
                    for i in range(add_rows, row_length + add_rows)]
        for i, (row, column) in enumerate(gs_range):
            try:
                name = self.args.subplots[i]
            except IndexError:
                break
            if len(self.args.subplots) == 1:
                subplot = self.fig.add_subplot(gs[row, :])
                self.subplot_borderaxespad = -3
            else:
                subplot = self.fig.add_subplot(gs[row, column])
            self.set_device_subplot_params(name, subplot)
            if self.args.x_datetime_format is not None:
                x_format = mdates.DateFormatter(self.args.x_datetime_format)
                subplot.xaxis.set_major_formatter(x_format)
            self.subplots[name] = subplot

    def _update_args_subplots(self):
        if self.args.cpu_only:
            return
        if not self.has_stat_data('device'):
            return
        columns = self.stats[0]['device']['columns']
        # TODO: check stats columns for all cases
        #       only PERCENT_IO_RQM in new iostat outputs at this time
        for col in ['%rrqm', '%wrqm']:
            if col in columns:
                return
        self.args.subplots.remove(PERCENT_IO_RQM)

    def set_device_subplot_params(self, name, subplot):
        if name == IO_RQM:
            subplot.set_title('io merged request counts per second')
            subplot.set_ylabel('counts')
        elif name == PERCENT_IO_RQM:
            subplot.set_title('percentage of requests merged together')
            subplot.set_ylabel('percent')
        elif name == IOPS:
            subplot.set_title('iops')
            subplot.set_ylabel('counts')
        elif name == IO_TRANSFER:
            subplot.set_title('io transer per second')
            subplot.set_ylabel('[M|K]Byte or Sector')
        elif name == PERCENT_UTIL:
            subplot.set_title('%util')
            subplot.set_ylabel('percent')
        elif name == AVGRQ_SZ:
            subplot.set_title('average size (in sectors) of the requests')
            subplot.set_ylabel('sectors')
        elif name == AVGQU_SZ:
            subplot.set_title('average queue length of the requests')
            subplot.set_ylabel('length')
        elif name == AWAIT:
            subplot.set_title('average time for i/o requests')
            subplot.set_ylabel('milliseconds')
        elif name == SVCTM:
            subplot.set_title('average service time')
            subplot.set_ylabel('milliseconds')
        else:
            raise NotImplementedError('unsupported subplot: %s' % name)

    def has_stat_data(self, target):
        return self.stats[0][target]['columns'] is not None

    def plot_cpu(self, x):
        if not self.has_stat_data('cpu'):
            return

        data = defaultdict(list)
        for stat in self.stats:
            cpu = stat['cpu']
            for i, column in enumerate(cpu['columns']):
                data[column].append(cpu['stat'][i])

        for column, values in data.items():
            self.cpu.plot(x, values, label=column)

        for vline in self.args.vlines:
            self.cpu.axvline(vline, linestyle=':', linewidth=3, color='purple')
        self.cpu.legend(
            bbox_to_anchor=(1.04, 0.5), loc='center left', borderaxespad=-3)

    def set_device_data(self, data, device):
        def set_data_value(data, columns, disk_stat_data):
            for col in columns:
                value = disk_stat_data.get(col)
                if value is not None:
                    data[name][disk_name + '_' + col].append(value)

        _disk_stat_data = {}
        for disk in device['stats']:
            for disk_name, disk_stat in disk.items():
                for i, column in enumerate(device['columns']):
                    _disk_stat_data[column] = disk_stat[i]
                for name in data:
                    if name == IO_RQM:
                        columns = ['rrqm/s', 'wrqm/s']
                    elif name == PERCENT_IO_RQM:
                        columns = ['%rrqm', '%wrqm']
                    elif name == IOPS:
                        columns = ['r/s', 'w/s']
                    elif name == IO_TRANSFER:
                        columns = [
                            'rMB/s', 'wMB/s',    # iostat -m
                            'rkB/s', 'wkB/s',    # iostat -k
                            'rsec/s', 'wsec/s',  # by default
                        ]
                    elif name == PERCENT_UTIL:
                        columns = ['%util']
                    elif name == AVGRQ_SZ:
                        columns = [
                            'avgrq-sz', 'areq-sz', 'rareq-sz', 'wareq-sz'
                        ]
                    elif name == AVGQU_SZ:
                        columns = ['avgqu-sz', 'aqu-sz']
                    elif name == AWAIT:
                        columns = ['await', 'r_await', 'w_await']
                    elif name == SVCTM:
                        columns = ['await', 'svctm']
                    else:
                        assert False
                    set_data_value(data, columns, _disk_stat_data)

    def plot_device(self, x):
        if not self.has_stat_data('device'):
            return

        data = {}
        for name in self.subplots:
            data[name] = defaultdict(list)

        for stat in self.stats:
            self.set_device_data(data, stat['device'])

        for name, device_data in data.items():
            for column, values in device_data.items():
                self.subplots[name].plot(x, values, label=column)

            for vline in self.args.vlines:
                self.subplots[name].axvline(
                    vline, linestyle=':', linewidth=3, color='purple',
                )
            self.subplots[name].legend(
                bbox_to_anchor=(1.04, 0.5), loc='center left',
                borderaxespad=self.subplot_borderaxespad
            )

    def plot(self):
        datetime_data = [i['date'] for i in self.stats]
        if not self.args.cpu_only:
            self.plot_device(datetime_data)
        if self.args.with_cpu:
            self.plot_cpu(datetime_data)
        if not self.args.cpu_only and self.args.with_cpu:
            plt.subplots_adjust(hspace=0.4)

    def show(self):
        plt.show(block=True)

    def save(self):
        plt.savefig(self.output)
