#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/12 17:41
@Author  : LCH
@File   : 3-消息提示模板拼接.py
"""
from langchain_core.prompts import ChatPromptTemplate

system_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请根据用户的提问进行回复，我叫{username}"),
])
human_prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}"),
])
prompt = system_prompt + human_prompt
print(prompt)
print(prompt.format(username="张三", query="你好,你是?"))
