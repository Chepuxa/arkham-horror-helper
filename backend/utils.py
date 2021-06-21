import asyncio

async def wrap_iter(iterable):
    loop = asyncio.get_event_loop()
    it = iter(iterable)

    DONE = object()
    def get_next_item():
        # Get the next item synchronously.  We cannot call next(it)
        # directly because StopIteration cannot be transferred
        # across an "await".  So we detect StopIteration and
        # convert it to a sentinel object.
        try:
            return next(it)
        except StopIteration:
            return DONE

    while True:
        # Submit execution of next(it) to another thread and resume
        # when it's done.  await will suspend the coroutine and
        # allow other tasks to execute while waiting.
        next_item = await loop.run_in_executor(None, get_next_item)
        if next_item is DONE:
            break
        yield next_item