#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/12 22:18
@Author  : LCH
@File   : 1-LLM与ChatModel使用技巧.py
"""
import os
from datetime import datetime

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
# 1.编排Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是Qwen开发的聊天机器人，请回答用户的问题，现在的时间是{now}"),
    ("human", "{query}"),
]).partial(now=datetime.now())

# 2.创建大语言模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 3.生成内容
prompt_value = prompt.invoke({"query": "现在是几点，请讲一个关于程序员的冷笑话"})
ai_message = llm.invoke(prompt_value)

# 4.提取内容
print("type:", ai_message.type)
print("content:", ai_message.content)
print("response_metadata:", ai_message.response_metadata)
