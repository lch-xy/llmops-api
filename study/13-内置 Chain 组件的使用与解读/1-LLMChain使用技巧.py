#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/23 20:39
@Author  : LCH
@File   : 1-LLMChain使用技巧.py
"""
import os

import dotenv
from langchain_classic.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}主题的冷笑话")

llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
)
chain = LLMChain(prompt=prompt, llm=llm)

# print(chain("程序员"))
# print(chain.run("程序员"))
# print(chain.apply([{"subject": "程序员"}]))
# print(chain.generate([{"subject": "程序员"}]))
# print(chain.predict(subject="程序员"))

print(chain.invoke({"subject": "程序员"}))
