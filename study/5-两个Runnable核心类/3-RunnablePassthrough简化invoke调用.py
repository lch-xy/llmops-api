#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 21:10
@Author  : LCH
@File   : 3-RunnablePassthrough简化invoke调用.py
"""
import os

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
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

# 4.编排链 assign只能接受dic的输入 LangChain 在运行时会“自动把 callable 包装成 RunnableLambda”
chain = RunnablePassthrough.assign(context=lambda x: retrieval(x["query"])) | prompt | llm | parser
# chain = RunnableParallel({
#     "context": retrieval,
#     "query": RunnablePassthrough(),
# }) | prompt | llm | parser

# 5.调用链
res = chain.invoke({"query": "我是谁？"})

print(res)
