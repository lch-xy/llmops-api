#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 20:10
@Author  : LCH
@File   : 2-RunnableParallel模拟检索.py
"""
import os
from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


def retrieval(query: str) -> str:
    print("正在检索中...", query)
    return "我叫张三"


# 1,编排prompt
prompt = ChatPromptTemplate.from_template("""请根据用户的问题回答，可以参考对应的上下文进行生产

<context>
{context}
</context>


用户的提问是：{query}""")

# 2.创建大语言模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 3.创建输出解释器
parser = StrOutputParser()

# 4.编排链 RunnableParallel可以拿掉 因为|会自动拼成RunnableParallel
chain = RunnableParallel({
    "context": lambda x: retrieval(x["query"]),
    "query": itemgetter("query")
}) | prompt | llm | parser

# 5.调用链
res = chain.invoke({"query": "我是谁？"})

print(res)
