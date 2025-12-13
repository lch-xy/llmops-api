#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 14:59
@Author  : LCH
@File   : 2-Model批处理.py
"""
import os

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.构建提示模板
prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话")

# 2.构建大语言模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 3.批处理获取响应
ai_messages = llm.batch([prompt.invoke({"subject": "医生"}), prompt.invoke({"subject": "程序员"})])

for ai_message in ai_messages:
    print("type:", ai_message.type)
    print("content:", ai_message.content)
    print("response_metadata:", ai_message.response_metadata)
    print("--------------------------------------------------------------------------------")
