#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/25 22:41
@Author  : LCH
@File   : 1-bind函数使用技巧.py
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", "你正在执行一项测试，请重复用户传递的内容，除了重复其他均不要操作"),
    ("human", "{query}")
])

llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
)

# 这种写法是吞掉整个生成段，如果要命中停止要自己手动去截取
# chain = prompt | llm.bind(stop="world") | StrOutputParser()
chain = prompt | llm | StrOutputParser()

# content = chain.invoke({"query": "Hello world"})
stop_word = "world"
buffer = ""
for chunk in (prompt | llm).stream({"query": "Hello world"}):
    buffer += chunk.content
    if stop_word in buffer:
        buffer = buffer.split(stop_word)[0]
        break
print(buffer)
