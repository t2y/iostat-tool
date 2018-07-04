import math
from collections import defaultdict

from matplotlib import pyplot as plt
from matplotlib import gridspec

from .consts import AVGRQ_SZ, AVGQU_SZ, AWAIT, SVCTM
from .consts import IO_RQM, IOPS, IO_TRANSFER, PERCENT_UTIL
from .renderer import Renderer
from .utils import get_logger

log = get_logger()
default_figsize = plt.rcParams.get('figure.figsize')


class Plotter(Renderer):

    def __init__(self, args, stats):
        self.args = args
        self.stats = stats

        figsize = args.figsize
        if figsize is None:
            figsize = (18, 14)

        self.fig = plt.figure(figsize=figsize)
        self.fig.suptitle('iostat output')

        row_length = math.ceil(len(args.subplots) / 2.0)
        gs = gridspec.GridSpec(row_length + 1, 2)

        self.cpu = self.fig.add_subplot(gs[0, :])
        self.cpu.set_title('cpu average')
        self.cpu.set_ylim(0, 100)
        self.cpu.set_ylabel('percent')

        self.subplots = {}
        gs_range = [(i, j) for j in (0, 1) for i in range(1, row_length + 1)]
        for i, (row, column) in enumerate(gs_range):
            try:
                name = args.subplots[i]
            except IndexError:
                break
            subplot = self.fig.add_subplot(gs[row, column])
            self.set_device_subplot_params(name, subplot)
            self.subplots[name] = subplot

    def set_device_subplot_params(self, name, subplot):
        if name == IO_RQM:
            subplot.set_title('io request queue merged')
            subplot.set_ylabel('counts')
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
        self.cpu.legend(loc=6)

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
                        columns = ['avgrq-sz']
                    elif name == AVGQU_SZ:
                        columns = ['avgqu-sz']
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
            self.subplots[name].legend(loc=6)

    def plot(self):
        datetime_data = [i['date'] for i in self.stats]
        self.plot_cpu(datetime_data)
        self.plot_device(datetime_data)
        plt.subplots_adjust(hspace=0.5)

    def show(self):
        plt.show(block=True)

    def save(self):
        plt.savefig(self.output)
