# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/21 13:28
@Author  : LCH
@File   : 1-断点实现人在环路示例.py
"""
import base64
import os
import time
from typing import TypedDict, Annotated, Any, Literal

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
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


class State(TypedDict):
    """图状态数据结构，类型为字典"""
    messages: Annotated[list, add_messages]


tools = [google_serper, dalle]
llm = ChatOpenAI(
    model="qwen3.5:4b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State, config: RunnableConfig) -> Any:
    """聊天机器人函数"""
    # 1.获取状态里存储的消息列表数据并传递给LLM
    ai_message = llm_with_tools.invoke(state["messages"])
    # 2.返回更新/生成的状态
    return {"messages": [ai_message]}


def route(state: State, config: RunnableConfig) -> Literal["tools", "__end__"]:
    """动态选择工具执行亦或者结束"""
    # 1.获取生成的最后一条消息
    ai_message = state["messages"][-1]
    # 2.检测消息是否存在tool_calls参数，如果是则执行`工具路由`
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    # 3.否则生成的内容是文本信息，则跳转到结束路由
    return END


# 1.创建状态图，并使用GraphState作为状态数据
graph_builder = StateGraph(State)

# 2.添加节点
graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

# 3.添加边
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("tools", "llm")
graph_builder.add_conditional_edges("llm", route)

# 4.编译图为Runnable可运行组件
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["tools"])

# 5.调用图架构应用
config = {"configurable": {"thread_id": 1}}
state = graph.invoke(
    {"messages": [("human", "2024年北京半程马拉松的前3名成绩是多少")]},
    config=config,
)
print(state)

# 6.进行人机交互
# 判断大模型是否真的想调用工具（比如它可能只是普通聊天，并没有触发工具）
if hasattr(state["messages"][-1], "tool_calls") and len(state["messages"][-1].tool_calls) > 0:

    # 打印出模型想调用的工具名称和参数，给人类审核
    print("现在准备调用工具: ", state["messages"][-1].tool_calls)

    # 【核心交互】阻塞程序，在控制台等待用户手动输入 yes 或 no
    human_input = input("如果需要执行工具请输入yes，否则请输入no: ")

    if human_input.lower() == "yes":
        # 【放行并继续执行】
        # 这里传入 None 是非常关键的！因为状态已经存在 checkpointer 的记忆里了。
        # 传入 None 加上之前的 thread_id (config)，告诉 LangGraph：“读取刚才暂停的状态，越过断点，继续往下跑！”
        print(graph.invoke(None, config)["messages"][-1].content)

    else:
        # 如果人类输入 no，就不再调用 graph.invoke，流程自然结束（拒绝执行工具）
        print("图程序执行完毕")
