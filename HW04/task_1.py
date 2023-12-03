import time
from threading import Thread
from multiprocessing import Process
from pathlib import Path

from fib import Fib


def get_threads_time(func, *args, num_threads):
    start_time = time.perf_counter_ns()
    threads = [None] * num_threads

    for i in range(num_threads):
        threads[i] = Thread(target=func, args=args)
        threads[i].start()

    for thread in threads:
        thread.join()

    end_time = time.perf_counter_ns()
    return end_time - start_time


def get_processes_time(func, *args, num_processes):
    start_time = time.perf_counter_ns()
    processes = [None] * num_processes

    for i in range(num_processes):
        processes[i] = Process(target=func, args=args)
        processes[i].start()

    for process in processes:
        process.join()

    end_time = time.perf_counter_ns()
    return end_time - start_time


def get_sync_time(func, *args):
    start_time = time.perf_counter_ns()

    func(*args)

    end_time = time.perf_counter_ns()
    return end_time - start_time


if __name__ == "__main__":
    N = 1000
    fib = Fib()

    sync_time = sum(get_sync_time(fib, N) for _ in range(10))
    threads_time = sum(get_threads_time(fib, N, num_threads=10) for _ in range(10))
    processes_time = sum(
        get_processes_time(fib, N, num_processes=10) for _ in range(10)
    )

    artifacts_dir = Path(__file__).parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    with (artifacts_dir / "task_1.txt").open(mode="w", encoding="utf-8") as f:
        f.write(f"Execution time with synchronous execution: {sync_time} ns\n")
        f.write(f"Execution time with threading: {threads_time} ns\n")
        f.write(f"Execution time with multiprocessing: {processes_time} ns\n")
