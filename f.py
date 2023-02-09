from flask import Flask
from flask import g

from func_blocking import cpu_bound_func
from loop import get_executor_flask
from config import ITERATIONS, MODE

if MODE == "process_pool":
    from concurrent.futures.process import ProcessPoolExecutor as PoolExecutor
elif MODE == "thread_pool":
    from concurrent.futures.thread import ThreadPoolExecutor as PoolExecutor

app = Flask(__name__)

def get_executor():
    if 'executor' not in g:
        g.executor = PoolExecutor()

    return g.executor

def get_pool_executor():
    if 'pool_executor' not in g:
        g.pool_executor = get_executor_flask(get_executor)

    return g.pool_executor


@app.route('/', methods=['GET', 'POST'])
async def index() -> str:
    if MODE == "blocking":
        cpu_bound_func(ITERATIONS)
    elif MODE == "process_pool" or "thread_pool":
        pool_executor = get_pool_executor()
        await pool_executor(cpu_bound_func, ITERATIONS)
    else:
        raise Exception(f"Unknown Mode. {MODE}")

    # python -m timeit "sum(range(100_000_000))"
    # Madhavas M2 Max: 1 loop, best of 5: 992 msec per loop
    cpu_bound_func(150_000_00)

    response = f"ok".encode("utf-8")
    print(response)
    return response, 200, {"content-type": "application/octect-stream"}

if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0", threaded=False, processes=10)


# export FLASK_ENV=development
# flask --app f.py run --host=0.0.0.0 --port=8080
# oha -n 60 -c 10 --latency-correction --disable-keepalive http://127.0.0.1:8080

# scalene --profile-all flask --app f.py run

