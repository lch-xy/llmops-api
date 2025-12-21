#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/23 15:32
@Author  : thezehui@gmail.com
@File    : 1.实体记忆组件示例.py
"""
import os

import dotenv
from langchain_classic.chains.conversation.base import ConversationChain
from langchain_classic.memory import ConversationEntityMemory
from langchain_classic.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    temperature=0
)

chain = ConversationChain(
    llm=llm,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    memory=ConversationEntityMemory(llm=llm),
)

print(chain.invoke({"input": "你好，我是慕小课。我最近正在学习LangChain。"}))
print(chain.invoke({"input": "我最喜欢的编程语言是 Python。"}))
print(chain.invoke({"input": "我住在广州"}))

# 查询实体中的对话
res = chain.memory.entity_store.store
print(res)
