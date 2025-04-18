import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Event, Manager


def calculate_fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    test_numbers = [1000000, 1000001, 1000002, 1000003, 1000004]
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        try:
            futures = {executor.submit(calculate_fibonacci, n): n for n in test_numbers}
            
            for future in as_completed(futures):
                if (result := future.result()) is not None:
                    print(f"结果: {str(result)[-6:]}")
                else:
                    print("任务被取消")
        except KeyboardInterrupt:
            print("用户强制终止")
            executor.shutdown(wait=False, cancel_futures=True)
            

from multiprocessing import Pool, Manager, Event

def calculate_fibonacci(n, event):
    a, b = 0, 1
    for _ in range(n):
        if event.is_set():  # 检查终止信号
            return None
        a, b = b, a + b
    return a

def main_2():
    test_numbers = [1000000, 1000001, 1000002, 1000003, 1000004]
    with Manager() as manager:
        event = manager.Event()
        pool = Pool(processes=4)
        try:
            results = [pool.apply_async(calculate_fibonacci, (n, event)) for n in test_numbers]
            for res in results:
                if (result := res.get()) is not None:
                    print(f"结果: {str(result)[-6:]}")
        except KeyboardInterrupt:
            print("用户强制终止")
            event.set()  # 发送终止信号
            pool.terminate()  # 立即终止所有子进程
        finally:
            pool.close()
            pool.join()
            

from joblib import Parallel, delayed
from multiprocessing import Manager
import time

def calculate_fibonacci(n, stop_event):
    a, b = 0, 1
    for _ in range(n):
        if stop_event.is_set():  # 检查终止信号
            print(f"任务 {n} 被终止")
            return None
        a, b = b, a + b
    return a

def main():
    test_numbers = [1000000, 1000001, 1000002, 1000003, 1000004]
    with Manager() as manager:
        stop_event = manager.Event()
        try:
            # 提交任务并绑定共享标记
            results = Parallel(n_jobs=8)(
                delayed(calculate_fibonacci)(n, stop_event)
                for n in test_numbers
            )
            for res in results:
                if res is not None:
                    print(f"结果: {str(res)[-6:]}")
        except KeyboardInterrupt:
            print("用户强制终止")
            stop_event.set()  # 设置终止标记

if __name__ == "__main__":
    main()
    