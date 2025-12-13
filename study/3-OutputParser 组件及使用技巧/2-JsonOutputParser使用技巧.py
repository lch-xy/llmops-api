#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 15:39
@Author  : LCH
@File   : 2-JsonOutputParser使用技巧.py
"""
import os

import dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

dotenv.load_dotenv()


# 1.构建出json输出格式
class Joke(BaseModel):
    joke: str = Field(description="回答用户的冷笑话")
    punchline: str = Field(description="冷笑话的笑点")


# 2.构建json输出解析器
parser = JsonOutputParser(pydantic_object=Joke)

# 3.编排提示词
promot = ChatPromptTemplate.from_template("回答用户的问题。\n{format_instructions}\n{query}\n").partial(
    format_instructions=parser.get_format_instructions())

# 4.构建大模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 5.调用模型
promot_value = promot.invoke({"query": "讲一个关于医生和患者之间的故事"})
print("promot_value", promot_value.to_string())
print("------------------------------------------------------------------------")

ai_message = llm.invoke(promot_value)
print("ai_message", ai_message)
print("------------------------------------------------------------------------")

joke_json = parser.invoke(ai_message)
print("joke_json", joke_json)
