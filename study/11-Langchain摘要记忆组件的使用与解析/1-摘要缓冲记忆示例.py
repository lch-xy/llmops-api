#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/19 21:21
@Author  : LCH
@File   : 1-缓冲窗口记忆示例.py
"""
import os
from operator import itemgetter

import dotenv
from langchain_classic.memory import ConversationSummaryBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.创建提示模板&记忆
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是聊天机器人，根据对应上下文回复用户问题"),
    MessagesPlaceholder("history"),
    ("human", "{query}"),
])

memory = ConversationSummaryBufferMemory(
    max_token_limit=300,
    return_messages=True,
    # input_key="query",  # 有多个输入的时候需要指定
    # output_key="output",  # 有多个输出的时候需要指定
    llm=ChatOpenAI(
        model="qwen3:8b",
        base_url=os.getenv("OPENAI_API_BASE_URL")
    )
)

# 2.创建大语言模型
# memory_variables = memory.load_memory_variables({})
# qwen等模型没有计算token的方法，会报错
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 3.构建链
chain = RunnablePassthrough.assign(
    history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
) | prompt | llm | StrOutputParser()

# 4.死循环构建对话命令行
while True:
    query = input("human：")

    if query == "q":
        exit(0)

    chain_input = {"query": query, "history": []}

    response = chain.stream(chain_input)

    print("AI：", end="", flush=True)
    output = ""
    for chunk in response:
        output += chunk
        print(chunk, end="", flush=True)
    memory.save_context(chain_input, {"output": output})
    print("")
    print("history:", memory.load_memory_variables({}))
