#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 15:32
@Author  : LCH
@File   : 1-StrOutputParser使用技巧.py
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.构建提示词
prompt = ChatPromptTemplate.from_template("{query}")

# 2.构建大语言模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 3.创建字符串输出解析器
parse = StrOutputParser()

# 4.调用大语言模型生产结果并解析
content = parse.invoke(llm.invoke(prompt.invoke({"query": "请讲一个关于程序员的冷笑话"})))

print(content)
