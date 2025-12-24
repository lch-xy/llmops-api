#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/23 20:40
@Author  : LCH
@File   : 3-对话链.py
"""
import os

import dotenv
from langchain_classic.chains.conversation.base import ConversationChain
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
)

chain = ConversationChain(llm=llm)

content = chain.invoke({"input": "你好，我是慕小课，我喜欢打篮球还有游泳，你喜欢什么运动呢？"})

print(content)

content = chain.invoke({"input": "根据上下文信息，请统计一下我的运动爱好有什么?"})

print(content)
