from fastapi import FastAPI

from func_blocking import cpu_bound_func
from loop import get_executor_fastapi
from config import ITERATIONS, MODE

if MODE == "process_pool":
    from concurrent.futures.process import ProcessPoolExecutor as PoolExecutor
elif MODE == "thread_pool":
    from concurrent.futures.thread import ThreadPoolExecutor as PoolExecutor

app = FastAPI()



if MODE == "process_pool" or MODE == "thread_pool":
    @app.on_event("startup")
    async def on_startup():
        app.state.executor = PoolExecutor()

if MODE == "process_pool" or MODE == "thread_pool":
    pool_executor = get_executor_fastapi(app)

@app.get("/")
async def root():
    if MODE == "blocking":
        cpu_bound_func(ITERATIONS)
    elif MODE == "process_pool" or "thread_pool":
        await pool_executor(cpu_bound_func, ITERATIONS)
    else:
        raise Exception(f"Unknown Mode. {MODE}")

    response = f"ok".encode("utf-8")
    print(response)
    return response, 200, {"content-type": "application/octect-stream"}

if MODE == "process_pool" or MODE == "thread_pool":
    @app.on_event("shutdown")
    async def on_shutdown():
        app.state.executor.shutdown()

# oha -n 60 -c 10 --latency-correction --disable-keepalive http://127.0.0.1:8080
# exec uvicorn --reload --host=0.0.0.0 --port=8080 fa:app
# scalene `which uvicorn` --host=0.0.0.0 --port=8080 --workers 1 fa:app
# python -m timeit "total = 150_000_00; import torch as th; x = th.tensor([range(total)]); x.sum()"
# Madhavas M2 Max: 1 loop, best of 5: 1.09 sec per loop
