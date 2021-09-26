"""
Running process asynchronously supports over Python 3.4,
so use generator based coroutine instead of native coroutine (async/await)
"""
import asyncio
import asyncio.subprocess

from .parser import Parser
from .scatter import Scatter
from .utils import get_logger

log = get_logger()


@asyncio.coroutine
def run_process(future, command_and_args, queue):
    create = asyncio.create_subprocess_exec(
        *command_and_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    proc = yield from create
    while True:
        line = yield from proc.stdout.readline()
        if queue.full():
            yield from asyncio.sleep(1)
        else:
            queue.put_nowait(line)

        # check process is finished or not,
        # but it might not occurred immediately
        # in that case, proc.stdout.readline() might return empty line
        # during several seconds
        if proc.returncode is not None:
            break

    future.set_result(proc.returncode)


@asyncio.coroutine
def read_stream(queue, args):
    parser = Parser(args)
    scatter = Scatter(args)
    with open(args.output, 'wb') as f:
        try:
            while True:
                if queue.empty():
                    yield from asyncio.sleep(1)
                else:
                    # TODO: it might miss rest of last queue entries
                    #       when the process finished
                    output = queue.get_nowait()
                    f.write(output)
                    line = output.decode()
                    print(line.rstrip())

                    for stat in parser.parse_line(line):
                        # note: get stat for previous date entry
                        if parser.filter(stat):
                            scatter.scatter(stat)
        except Exception:
            if args.backend == 'Agg':
                scatter.save()


def cancel_tasks():
    # TODO: confirm detailed behavior
    for task in asyncio.Task.all_tasks():
        task.cancel()


def finish_tasks(future):
    status_code = future.result()
    if status_code != 0:
        log.error('process was not finished normally: %d', status_code)
    cancel_tasks()


def run_iostat(args):
    command_and_args = ['iostat'] + args.iostat_args.split()
    log.debug(command_and_args)
    event_loop = asyncio.get_event_loop()
    future = asyncio.Future()
    queue = asyncio.Queue(maxsize=args.max_queue_size, loop=event_loop)
    asyncio.ensure_future(run_process(future, command_and_args, queue))
    future.add_done_callback(finish_tasks)
    try:
        event_loop.run_until_complete(read_stream(queue, args))
        event_loop.run_forever()
    except KeyboardInterrupt:
        cancel_tasks()
    except asyncio.CancelledError:
        pass
    finally:
        event_loop.close()
