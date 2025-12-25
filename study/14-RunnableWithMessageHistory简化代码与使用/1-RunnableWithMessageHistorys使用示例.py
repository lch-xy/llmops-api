#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/24 19:45
@Author  : LCH
@File   : 1-RunnableWithMessageHistorys使用示例.py
"""
import os

import dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.定义历史存储记忆
store = {}


# 2.工厂函数，用于获取知道那个会话的历史聊天
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = FileChatMessageHistory(
            f"chat_history_{session_id}.txt"
        )
    return store[session_id]


# 3.构建提示模板与大语言模型
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，能根据用户的提问回复问题"),
    MessagesPlaceholder("history"),
    ("human", "{query}")
])
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 4.构建链
chain = prompt | llm | StrOutputParser()

# 5.包装链
with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="query",
    history_messages_key="history"
)

while True:
    query = input("human：")

    if query == "q":
        exit(0)

    # 6.运行链并传递配置信息
    response = with_message_history.stream(
        {"query": query},
        config={"configurable": {"session_id": "zhangsan"}}
    )

    print("AI：", end="", flush=True)
    for chunk in response:
        print(chunk, end="", flush=True)
    print("")
