#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/12 11:15
@Author  : LCH
@File   : 1-Prompt组件基础用法.py
"""
from datetime import datetime

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

prompt = PromptTemplate.from_template("请讲一个关于{subject}冷笑话")
print(prompt.format(subject="猫"))
prompt_value = prompt.invoke({"subject": "狗"})
print(prompt_value.to_string())
print(prompt_value.to_messages())

print(
    "----------------------------------------------------------------------------------------------------------------")

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是聊天机器人,当前时间{now}"),
    # 有时候还有其他的消息
    MessagesPlaceholder("chat_history"),
    HumanMessagePromptTemplate.from_template("请讲一个关于{subject}冷笑话")
]).partial(now=datetime.now)

chat_prompt_value = chat_prompt.invoke({
    "chat_history": [
        ("human", "我叫张三"),
        AIMessage("你是谁"),
    ],
    "subject": "狗", }
)
print(chat_prompt_value)
