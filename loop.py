import asyncio

def get_executor_robyn(executor):
    async def run_in_loop(fn, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, fn, *args)  # wait and return result
    return run_in_loop

def get_executor_fastapi(app):
    async def run_in_loop(fn, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(app.state.executor, fn, *args)  # wait and return result
    return run_in_loop

def get_executor_flask(g):
    async def run_in_loop(fn, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(g(), fn, *args)  # wait and return result
    return run_in_loop


