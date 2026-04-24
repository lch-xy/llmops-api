#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/21 11:33
@Author  : LCH
@File   : 1-MemorySaver实现记忆持久化.py
"""
import base64
import os
import time

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic.v1 import BaseModel, Field

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


# 1.定义工具与工具列表
google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)


class OllamaImageGenerationTool(BaseTool):
    name: str = "ollama_image_gen"
    description: str = (
        "使用 Ollama 本地模型生成图像的工具。"
        "输入应该是生成图像的文本提示(prompt)。"
    )
    args_schema: type[BaseModel] = DallEArgsSchema

    def _run(self, query: str) -> str:
        url = "http://localhost:11434/v1/images/generations"
        payload = {
            "model": "x/flux2-klein",
            "prompt": query,
            "response_format": "b64_json"
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            res_data = response.json()

            # 1. 提取 Base64 数据
            b64_data = res_data['data'][0]['b64_json']

            # 2. 保存为本地图片文件（当前文件夹）
            file_name = f"img_{int(time.time())}.png"
            with open(file_name, "wb") as f:
                f.write(base64.b64decode(b64_data))

            # 3. 打印路径并返回给模型
            print(f"图片已生成并保存至当前文件夹: {file_name}")
            return f"图像生成成功，文件名为: {file_name}"
        except Exception as e:
            return f"图像生成失败: {str(e)}"


dalle = OllamaImageGenerationTool()

tools = [google_serper, dalle]

# 2.创建大语言模型
model = ChatOpenAI(
    model="qwen3.5:4b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    temperature=0
)

# 3.使用预构建的函数创建ReACT智能体
checkpointer = MemorySaver()
config_one = {"configurable": {"thread_id": 1}}
config_two = {"configurable": {"thread_id": 2}}
agent = create_react_agent(model=model, tools=tools, checkpointer=checkpointer)

# 4.调用智能体并输出内容
print(agent.invoke(
    {"messages": [("human", "你好，我叫慕小课，我喜欢游泳打球，你喜欢什么呢?")]},
    config=config_one,
))

# 5.二次调用检测图结构程序是否存在记忆
print(agent.invoke(
    {"messages": [("human", "你知道我叫什么吗?")]},
    config=config_two
))
