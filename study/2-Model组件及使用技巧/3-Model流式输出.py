#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 15:06
@Author  : LCH
@File   : 3-Model流式输出.py
"""
import os

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.编排prompt
prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话")

# 2.构建大模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 3.流式输出
rep = llm.stream(prompt.invoke({"subject": "医生"}))

for chunk in rep:
    print(chunk.content, flush=True, end="")
