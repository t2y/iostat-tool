from functools import partial


def filter_since(since_date, stat):
    return since_date <= stat['date']


def filter_until(until_date, stat):
    return stat['date'] <= until_date


def filter_disks(disk_names, stat):
    filtered = []
    for disk in stat['device']['stats']:
        for name in disk:
            if name in disk_names:
                filtered.append(disk)
    stat['device']['stats'] = filtered
    return True


def get_filters(args):
    filters = []
    if args.since is not None:
        filters.append(partial(filter_since, args.since))
    if args.until is not None:
        filters.append(partial(filter_until, args.until))
    if args.disks:
        filters.append(partial(filter_disks, args.disks))
    return filters
