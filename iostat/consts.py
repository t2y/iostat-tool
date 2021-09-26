PACKAGE_NAME = 'iostat-tool'

# parser options
SUB_COMMAND_CSV = 'csv'
SUB_COMMAND_MONITOR = 'monitor'
SUB_COMMAND_PLOT = 'plot'

# plot options
PLOT_TYPE_PLOTTER = 'plotter'
PLOT_TYPE_SCATTER = 'scatter'
PLOT_TYPES = [
    PLOT_TYPE_PLOTTER,
    PLOT_TYPE_SCATTER,
]

# device subplots parameters
IO_RQM = 'io_rqm'
PERCENT_IO_RQM = '%io_rqm'
IOPS = 'iops'
IO_TRANSFER = 'io_transfer'
PERCENT_UTIL = '%util'
AVGRQ_SZ = 'avgrq-sz'
AVGQU_SZ = 'avgqu-sz'
AWAIT = 'await'
SVCTM = 'svctm'

DEVICE_SUBPLOTS = [
    IO_RQM, PERCENT_IO_RQM,
    IOPS, IO_TRANSFER, PERCENT_UTIL,
    AVGRQ_SZ, AVGQU_SZ, AWAIT, SVCTM,
]
