from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from matplotlib import gridspec

from .renderer import Renderer


class Scatter(Renderer):

    def __init__(self, args):
        self.args = args
        self.closed = False
        self.start_date = args.since
        if self.start_date is None:
            self.start_date = datetime.now()

        figsize = args.figsize
        if figsize is None:
            figsize = (18, 13)

        self.fig = plt.figure(figsize=figsize)
        self.fig.suptitle('iostat scatter')
        self.fig.canvas.mpl_connect('close_event', self.close_handler)

        self.row_length = 5
        self.init_cpu()
        self.init_device()

    def close_handler(self, event):
        # FIXME: how to exit forcely
        self.closed = True
        plt.close(self.fig)
        raise SystemExit

    def init_cpu(self):
        self.cpus = []
        items = ['%user', '%nice', '%system', '%iowait', '%steal', '%idle']
        for i, item in enumerate(items, 1):
            subplot = self.fig.add_subplot(self.row_length, 6, i)
            subplot.set_title(item)
            subplot.set_ylabel('percent')
            self.cpus.append(subplot)

    def init_device(self):
        items = [
            'rrqm/s', 'wrqm/s', 'r/s', 'w/s',
            'r[MB|kB|sec]/s', 'w[MB|kB|sec]/s', 'avgrq-sz', 'avgqu-sz',
            'await', 'r_await', 'w_await', 'svctm',
        ]

        step = 4
        self.devices = []
        for num in range(0, len(items), step):
            for i, item in enumerate(items[num:num + step], 1):
                loc = i + num + step
                subplot = self.fig.add_subplot(self.row_length, step, loc)
                subplot.set_title(item)
                self.devices.append(subplot)

        gs = gridspec.GridSpec(self.row_length, 6)
        subplot = self.fig.add_subplot(gs[self.row_length - 1, :])
        subplot.set_title('%util')
        self.devices.append(subplot)

    def scatter_cpu(self, date, stat):
        if stat['columns'] is None:
            return

        end_date = date + timedelta(seconds=2)
        for i, column in enumerate(stat['columns']):
            self.cpus[i].scatter(date, stat['stat'][i])
            self.cpus[i].axis([self.start_date, end_date, 0, 100])

    def scatter_device(self, date, device):
        if device['columns'] is None:
            return

        end_date = date + timedelta(seconds=2)
        for i, column in enumerate(device['columns']):
            for disk in device['stats']:
                for disk_name, disk_stat in disk.items():
                    self.devices[i].set_xlim(self.start_date, end_date)
                    self.devices[i].scatter(date, disk_stat[i])

    def scatter(self, stat):
        if self.closed:
            return

        date = stat['date']
        self.scatter_cpu(date, stat['cpu'])
        self.scatter_device(date, stat['device'])
        plt.pause(0.001)
        plt.subplots_adjust(wspace=0.4, hspace=0.4)

    def set_vlines(self):
        if not hasattr(self.args, 'vlines'):
            return

        for vline in self.args.vlines:
            for cpu in self.cpus:
                cpu.axvline(vline, linestyle=':', linewidth=3, color='purple')
            for dev in self.devices:
                dev.axvline(vline, linestyle=':', linewidth=3, color='purple')

    def show(self):
        self.set_vlines()
        plt.show(block=True)

    def save(self):
        self.set_vlines()
        plt.savefig(self.output)
