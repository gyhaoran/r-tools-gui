# main.py
from algorithm import fast_sum

from array import array
import timeit


def sum(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
    

def main():
    int_array = array('i', range(50000000))  # 'i' 表示有符号整数
    result = fast_sum(int_array)  # 正确调用
    print(f"Result: {result}")  # 输出结果
    

def main_python():
    int_array = array('i', range(50000000))  # 'i' 表示有符号整数
    result = sum(int_array)  # 调用 Python 实现的 sum 函数
    print(f"Result: {result}")  # 输出结果

if __name__ == "__main__":
    # 运行主函数
    print("Cython 耗时：", timeit.timeit(main, number=1))
    print("Python 耗时：", timeit.timeit(main_python, number=1))
    