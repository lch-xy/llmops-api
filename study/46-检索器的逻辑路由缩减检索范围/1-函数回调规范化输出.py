#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/23 11:16
@Author  : LCH
@File   : 1-函数回调规范化输出.py
"""
import os
from typing import Literal

import dotenv
from langchain_openai import ChatOpenAI
from pydantic import Field, BaseModel

dotenv.load_dotenv()


class RouteQuery(BaseModel):
    """将用户查询映射到对应的数据源上"""
    datasource: Literal["python_docs", "js_docs", "golang_docs"] = Field(
        description="根据用户的问题，选择哪个数据源最相关以回答用户的问题"
    )


# 1.创建绑定结构化输出的大语言模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    temperature=0
)
structured_output = llm.with_structured_output(RouteQuery)

# 2.构建一个问题
question = """为什么下面的代码不工作了，请帮我检查下：

var a = "123"
"""
res: RouteQuery = structured_output.invoke(question)

print(res)
print(type(res))
print(res.datasource)
