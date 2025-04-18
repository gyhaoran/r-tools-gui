# setup.py
import sys
import shutil
from setuptools import setup, find_packages
from Cython.Build import cythonize
from Cython.Distutils import build_ext

# 编译配置
COMPILE_MAIN = True  # 是否编译 main.py
OUTPUT_DIR = "lib"   # 输出目录

class CustomBuildExt(build_ext):
    def run(self):
        super().run()
        # 将编译后的文件移动到指定目录
        if self.inplace:
            return
        for output in self.get_outputs():
            if output.endswith(".so") or output.endswith(".pyd"):
                dest = os.path.join(OUTPUT_DIR, os.path.basename(output))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(output, dest)

if COMPILE_MAIN:
    ext_modules = cythonize(
        "main.py",
        compiler_directives={
            "language_level": "3",    # 指定Python3
            "optimize.use_switch": True,
            "optimize.unpack_method_calls": True
        },
        build_dir="src"              # 生成中间文件到src目录
    )
else:
    ext_modules = []

setup(
    name="compiled_main",
    cmdclass={"build_ext": CustomBuildExt},
    ext_modules=ext_modules,
    script_args=["build_ext", "--inplace"],  # 关键参数
    packages=find_packages(exclude=["src", "lib"])
)
