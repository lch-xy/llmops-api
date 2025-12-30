#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/30 21:22
@Author  : LCH
@File   : 1-Runnable 重试机制.py
"""
from langchain_core.runnables import RunnableLambda

counter = -1


def func(x):
    global counter
    counter += 1
    print("正在执行第", counter, "次")
    return x / counter


chain = RunnableLambda(func).with_retry(stop_after_attempt=2)
resp = chain.invoke(2)
print(resp)
