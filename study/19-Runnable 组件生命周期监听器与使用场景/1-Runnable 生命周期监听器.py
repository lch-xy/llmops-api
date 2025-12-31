#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/31 14:57
@Author  : LCH
@File   : 1-Runnable 生命周期监听器.py
"""
import time

from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tracers import Run


def on_start(run_obj: Run, config: RunnableConfig):
    print("on_start")
    print("run_obj", run_obj)
    print("config", config)
    print("===================")


def on_end(run_obj: Run, config: RunnableConfig):
    print("on_end")
    print("run_obj", run_obj)
    print("config", config)
    print("====================")


def on_error(run_obj: Run, config: RunnableConfig):
    print("on_error")
    print("run_obj", run_obj)
    print("config", config)
    print("====================")


runnable = RunnableLambda(lambda x: time.sleep(x))
chain = runnable.with_listeners(on_start=on_start, on_end=on_end, on_error=on_error)

chain.invoke(2)
