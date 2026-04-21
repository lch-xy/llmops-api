#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/13 09:54
@Author  : LCH
@File   : 1-基于工具调用的Agent.py
"""
import base64
import os
import time

import dotenv
import requests
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
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

# 2.定义工具调用agent提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是由OpenAI开发的聊天机器人，善于帮助用户解决问题。"),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 3.创建大语言模型
llm = ChatOpenAI(
    model="qwen3.5:4b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    temperature=0
)

# 4.创建agent与agent执行者
agent = create_tool_calling_agent(
    prompt=prompt,
    llm=llm,
    tools=tools,
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print(agent_executor.invoke({"input": "帮我绘制一幅鲨鱼在天上游泳的场景"}))
