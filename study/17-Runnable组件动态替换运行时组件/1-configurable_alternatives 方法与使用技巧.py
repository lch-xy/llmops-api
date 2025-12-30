#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/30 21:02
@Author  : LCH
@File   : 1-configurable_alternatives 方法与使用技巧.py
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.创建提示词模板&定义默认llm
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
).configurable_alternatives(
    ConfigurableField(id="llm"),
    gpt=ChatOpenAI(model="gpt-oss:20b", base_url=os.getenv("OPENAI_API_BASE_URL")),
)

# 2.构建链应用
chain = prompt | llm | StrOutputParser()

# 3.调用链并船体配置参数
content = chain.invoke(
    {"query": "你是什么模型？"},
    config={
        "configurable": {
            "llm": "gpt"
        }
    }
)
print(content)
