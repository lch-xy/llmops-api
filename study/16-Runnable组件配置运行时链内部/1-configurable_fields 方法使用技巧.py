#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/29 20:11
@Author  : LCH
@File   : 1-configurable_fields 方法使用技巧.py
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.创建提示词模板
prompt = PromptTemplate.from_template("请生成一个小于{x}的随机整数")

# 2.创建llm
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
).configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
        name="llm的temperature参数",
        description="llm的description参数",
    )
)

# 3.构建链
chain = prompt | llm | StrOutputParser()

# 4.正常调试内容
content = chain.invoke({"x": 1000})
print(content)

print("------------------------------------------")

content = chain.with_config(configurable={"llm_temperature": 0}).invoke({"x": 1000})
# content = chain.invoke(
#     {"x": 1000},
#     config={
#         "configurable": {
#             "llm_temperature": 0
#         }
#     }
# )
print(content)
