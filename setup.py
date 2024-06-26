# -*- coding: utf-8 -*-
"""
@Time ： 2023/8/7 16:18
@Auth ： YD
@File ：setup.py.py
@IDE ：PyCharm
@Description ：cx_freeze打包
"""
import sys
from cx_Freeze import setup, Executable

# 设置脚本的名称和版本号
script_name = "main.py"
script_version = "2.0.1"
icon = "icon.ico"

# 创建可执行文件的配置
executables = [Executable(script_name, icon=icon, base="Win32GUI")]

# 设置构建选项
build_options = {
    "packages": ["PyQt5", "urllib.parse", "re", "requests", "sqlalchemy"],  # 需要包含的额外模块
    # "excludes": ["tkinter"],  # 需要排除的模块
    "include_files": ["ApiInfo.db"],  # 需要包含的其他文件
    "optimize": 2,  # 优化级别，0为不优化，2为最高优化
    "include_msvcr": True,  # 是否包含MSVC运行时库
    "silent": True,  # 构建过程中是否输出信息
    "zip_include_packages": ["*"],  # 压缩所有包
    "zip_exclude_packages": [],  # 不排除任何包
}


# 执行构建
setup(
    name=script_name,
    version=script_version,
    description="API 管理工具",
    options={"build_exe": build_options},
    executables=executables,

)