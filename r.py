from robyn import Robyn
from robyn.robyn import Response

from func_blocking import cpu_bound_func
from loop import get_executor_robyn
from config import ITERATIONS, MODE

if MODE == "process_pool":
    from concurrent.futures.process import ProcessPoolExecutor as PoolExecutor
elif MODE == "thread_pool":
    from concurrent.futures.thread import ThreadPoolExecutor as PoolExecutor

if MODE == "process_pool" or MODE == "thread_pool":
    executor = PoolExecutor()
    pool_executor = get_executor_robyn(executor)

app = Robyn(__file__)

counter = 0

@app.get("/")
async def h(request):
    global counter
    counter += 1
    print("counter", counter)
    if MODE == "blocking":
        await cpu_bound_func(ITERATIONS)
    elif MODE == "process_pool" or "thread_pool":
        await pool_executor(cpu_bound_func, ITERATIONS)
    else:
        raise Exception(f"Unknown Mode. {MODE}")

    
    response = f"ok {counter}".encode("utf-8")
    print(response)

    return Response(
        status_code=200,
        headers={"Content-Type": "application/octet-stream"},
        body=response,
    )

app.start(port=8080)

# scalene --profile-all python r.py --processes 10