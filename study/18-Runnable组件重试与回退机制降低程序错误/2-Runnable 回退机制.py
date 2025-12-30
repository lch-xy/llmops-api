#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/30 21:22
@Author  : LCH
@File   : 2-Runnable 回退机制.py
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.构建prompt和llm，并引发错误
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
).with_fallbacks(
    [
        ChatOpenAI(
            model="gpt-oss:20b",
            base_url=os.getenv("OPENAI_API_BASE_URL")
        )
    ]
)

# 2.构建链应用
chain = prompt | llm | StrOutputParser()

# 3.调用链并输出结果
content = chain.invoke({"query": "你是什么模型？"})
print(content)
