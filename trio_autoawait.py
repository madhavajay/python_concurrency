# Use with:
# %autoawait trio_autoawait.run_in_trio
#
# Additional control:
# import trio_autoawait
# trio_autoawait.stop()   # stop the Trio run
# trio_autoawait.start()  # start it -- restart if already running
#
# Ctrl+C works.

import trio, outcome, queue, signal

requests = queue.SimpleQueue()
cancel_run = trio.CancelScope()
cancel_cell = trio.CancelScope()

def run_in_trio(coro):
    global cancel_cell
    cancel_cell = trio.CancelScope()
    try:
        trio.current_time()
    except RuntimeError:
        start()

    @trio.lowlevel.disable_ki_protection
    async def wrapper_unprotected():
        with cancel_cell:
            return await coro

    async def wrapper():
        requests.put(("return", await outcome.acapture(wrapper_unprotected)))

    trio.lowlevel.spawn_system_task(wrapper)

    while True:
        kind, arg = requests.get()
        if kind == "return":
            return arg.unwrap()
        elif kind == "run":
            arg()
        elif kind == "finish":
            try:
                arg.unwrap()
            finally:
                raise RuntimeError(f"Trio run terminated unexpectedly: {arg}")

def drain():
    while True:
        kind, arg = requests.get()
        if kind == "return":
            try:
                arg.unwrap()
            finally:
                raise RuntimeError(f"Previous cell result was never collected: {arg}")
        elif kind == "run":
            arg()
        elif kind == "finish":
            return arg.unwrap()

def interrupt_ipython_or_trio(sig, frame):
    while frame is not None:
        if frame.f_code is run_in_trio.__code__:
            if trio.lowlevel.currently_ki_protected():
                cancel_cell.cancel()
                return
            break
        frame = frame.f_back
    raise KeyboardInterrupt

async def manage_runner():
    with cancel_run:
        old_handler = signal.signal(signal.SIGINT, interrupt_ipython_or_trio)
        try:
            requests.put(("finish", outcome.Value(None)))
            await trio.sleep_forever()
        finally:
            signal.signal(signal.SIGINT, old_handler)

def start():
    try:
        trio.current_time()
    except RuntimeError:
        pass
    else:
        stop()

    global cancel_run
    cancel_run = trio.CancelScope()
    trio.lowlevel.start_guest_run(
        manage_runner,
        run_sync_soon_threadsafe=lambda thunk: requests.put(("run", thunk)),
        done_callback=lambda result: requests.put(("finish", result)),
    )
    drain()

def stop():
    try:
        trio.current_time()
    except RuntimeError:
        return
    cancel_run.cancel()
    return drain()

start()