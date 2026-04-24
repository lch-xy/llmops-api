#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/20 19:39
@Author  : LCH
@File   : 1-条件边与循环构建工具调用Agent.py
"""

import base64
import json
import os
import time
from typing import TypedDict, Annotated, Any, Literal

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from pydantic.v1 import BaseModel, Field

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    prompt: str = Field(description="生成图像的文本提示(prompt)")


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

    def _run(self, prompt: str) -> str:
        url = "http://localhost:11434/v1/images/generations"
        payload = {
            "model": "x/flux2-klein",
            "prompt": prompt,
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


class State(TypedDict):
    """图状态数据结构，类型为字典"""
    messages: Annotated[list, add_messages]


tools = [google_serper, dalle]
llm = ChatOpenAI(
    model="qwen3.5:4b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State, config: RunnableConfig) -> Any:
    """聊天机器人函数"""
    # 1.获取状态里存储的消息列表数据并传递给LLM
    ai_message = llm_with_tools.invoke(state["messages"])
    # 2.返回更新/生成的状态
    return {"messages": [ai_message]}


def tool_executor(state: State, config: RunnableConfig) -> Any:
    """工具执行节点"""
    # 1.提取数据状态中的tool_calls
    tool_calls = state["messages"][-1].tool_calls

    # 2.根据找到的tool_calls去获取需要执行什么工具
    tools_by_name = {tool.name: tool for tool in tools}

    # 3.执行工具得到对应的结果
    messages = []
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        messages.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=json.dumps(tool.invoke(tool_call["args"])),
            name=tool_call["name"]
        ))

    # 4.将工具的执行结果作为工具消息更新到数据状态机中
    return {"messages": messages}


def route(state: State, config: RunnableConfig) -> Literal["tool_executor", "__end__"]:
    """通过路由来取检测下后续的返回节点是什么，返回的节点有2个，一个是工具执行，一个是结束节点"""
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tool_executor"
    return END


# 1.创建状态图，并使用GraphState作为状态数据
graph_builder = StateGraph(State)

# 2.添加节点
graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tool_executor", tool_executor)

# 3.添加边
graph_builder.set_entry_point("llm")
graph_builder.add_conditional_edges("llm", route)
graph_builder.add_edge("tool_executor", "llm")

# 4.编译图为Runnable可运行组件
graph = graph_builder.compile()

# 5.调用图架构应用
state = graph.invoke({"messages": [("human", "2024年北京半程马拉松的前3名成绩是多少")]})

for message in state["messages"]:
    print("消息类型: ", message.type)
    if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
        print("工具调用参数: ", message.tool_calls)
    print("消息内容: ", message.content)
    print("=====================================")
