#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/28 10:25
@Author  : LCH
@File   : helper.py
"""
import importlib
from typing import Any


def dynamic_import(module_name: str, symbol_name: str) -> Any:
    """动态导入特定模块下的特定功能

       举个例子：如果我们传 module_name="json", symbol_name="loads"
       它就会在内存里自动帮你执行: from json import loads
       并把 loads 这个函数返回给你。
    """
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)
