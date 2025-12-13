#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 17:17
@Author  : LCH
@File   : 1-手写chain实现简易版本.py
"""
import os
from typing import Any

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.构建组件
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)
parser = StrOutputParser()


# 2.定义一个链
class Chain:
    steps: list = []

    def __init__(self, steps: list):
        self.steps = steps

    def invoke(self, input: Any) -> Any:
        output: Any = input
        for step in self.steps:
            output = step.invoke(output)
            print("步骤：", step)
            print("输出:", output)
            print("===================")
        return output


# 3.编排链
chain = Chain([prompt, llm, parser])

# 4.输出结果
print(chain.invoke({"query": "你好"}))
