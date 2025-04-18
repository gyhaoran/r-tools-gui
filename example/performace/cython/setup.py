from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "algorithm.pyx",  # 指定编译文件
        annotate=True,    # 生成优化报告
        compiler_directives={'language_level': "3"}  # 指定Python3
    )
)
