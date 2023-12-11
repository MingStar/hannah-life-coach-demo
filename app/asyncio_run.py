# The following code is modified from asyncio\runner.py
# for adding scheduling logic

from asyncio import coroutines, events, tasks


def asyncio_run(main, set_schedulers, *, debug=None):  # type: ignore[no-untyped-def]
    """This method is from asyncio\runner.py

    Modified to add scheduling logic
    """

    if not coroutines.iscoroutine(main):
        raise ValueError("a coroutine was expected, got {!r}".format(main))

    loop = events.new_event_loop()
    try:
        set_schedulers(loop)
        events.set_event_loop(loop)
        if debug is not None:
            loop.set_debug(debug)
        return loop.run_until_complete(main)
    finally:
        try:
            _cancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            events.set_event_loop(None)
            loop.close()


def _cancel_all_tasks(loop):  # type: ignore[no-untyped-def]
    to_cancel = tasks.all_tasks(loop)
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(tasks.gather(*to_cancel, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )
