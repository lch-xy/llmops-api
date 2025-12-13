#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/12 17:36
@Author  : LCH
@File   : 2-字符串提示拼接.py
"""
from langchain_core.prompts import PromptTemplate

prompt = (
    # 用+号拼接一定要保证是个提示模板
        PromptTemplate.from_template("请将一个关于{subject}的冷笑话") + "，让我开心下" + "\n使用{language}语言。"
)
print(prompt)
print(prompt.format(subject="程序员", language="中文"))
