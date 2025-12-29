#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/29 19:55
@Author  : LCH
@File   : 2-bind解决RunnableLambda函数多参数的场景.py
"""
import random

from langchain_core.runnables import RunnableLambda


def get_weather(city: str, unit: str) -> str:
    """获取天气"""
    print(f"正在获取{city}的天气...单位为{unit}")
    return f"{city}的天气为{random.randint(10, 40)}{unit}。"


# get_weather_runnable = RunnableLambda(get_weather)
# resp = get_weather_runnable.invoke({"location": "上海", "unit": "摄氏度"})

get_weather_runnable = RunnableLambda(get_weather).bind(unit="摄氏度")
print(get_weather_runnable.kwargs)
resp = get_weather_runnable.invoke("上海")

print(resp)
