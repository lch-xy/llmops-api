#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/8 21:39
@Author  : LCH
@File   : 1-GPT模型绑定函数.py
"""
import json
import os
from typing import Type, Any

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic.v1 import Field, BaseModel

dotenv.load_dotenv()


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市，例如：广州")


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class GaodeWeatherTool(BaseTool):
    """根据传入的城市名查询天气"""
    name: str = "gaode_weather"
    description: str = "当你想询问天气或与天气相关的问题时的工具。"
    args_schema: Type[BaseModel] = GaodeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """运行工具获取对应城市的天气预报"""
        try:
            # 1.获取高德API秘钥，如果没有则抛出错误
            gaode_api_key = os.getenv("GAODE_API_KEY")
            if not gaode_api_key:
                return f"高德开放平台API秘钥未配置"

            # 2.提取传递的城市名字并查询行政编码
            city = kwargs.get("city", "")
            session = requests.session()
            api_domain = "https://restapi.amap.com/v3"
            city_response = session.request(
                method="GET",
                url=f"{api_domain}/config/district?keywords={city}&subdistrict=0&extensions=all&key={gaode_api_key}",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            city_response.raise_for_status()
            city_data = city_response.json()

            # 3.提取行政编码调用天气预报查询接口
            if city_data.get("info") == "OK":
                if len(city_data.get("districts")) > 0:
                    ad_code = city_data["districts"][0]["adcode"]

                    weather_response = session.request(
                        method="GET",
                        url=f"{api_domain}/weather/weatherInfo?city={ad_code}&extensions=all&key={gaode_api_key}&output=json",
                        headers={"Content-Type": "application/json; charset=utf-8"},
                    )
                    weather_response.raise_for_status()
                    weather_data = weather_response.json()
                    if weather_data.get("info") == "OK":
                        return json.dumps(weather_data)

            session.close()
            return f"获取{kwargs.get('city')}天气预报信息失败"
            # 4.整合天气预报信息并返回
        except Exception as e:
            return f"获取{kwargs.get('city')}天气预报信息失败"


# 1.定义工具列表
gaode_weather = GaodeWeatherTool()
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
tool_dict = {
    gaode_weather.name: gaode_weather,
    google_serper.name: google_serper,
}
tools = [tool for tool in tool_dict.values()]

# 2.创建Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "你是由OpenAI开发的聊天机器人，可以帮助用户回答问题，必要时刻请调用工具帮助用户解答，如果问题需要多个工具回答，请一次性调用所有工具，不要分步调用"
    ),
    ("human", "{query}"),
])

# 3.创建大语言模型并绑定工具 - 修改为Qwen模型
# 确保在 .env 文件中配置了：
# OPENAI_API_KEY=your_api_key (如果服务端需要)
# OPENAI_API_BASE_URL=http://your-ollama-or-api-server/v1

llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 4.检查模型是否支持工具调用
try:
    # 绑定工具
    llm_with_tool = llm.bind_tools(tools=tools)

    # 测试工具调用
    test_response = llm_with_tool.invoke("测试工具绑定")
    if hasattr(test_response, 'tool_calls'):
        print("✓ 模型支持工具调用")
    else:
        print("⚠ 模型可能不支持标准工具调用格式")
        # 如果不支持，可能需要特殊处理
        llm_with_tool = llm
except Exception as e:
    print(f"⚠ 工具绑定失败: {e}")
    print("将使用不绑定工具的模型")
    llm_with_tool = llm

# 4.创建链应用
chain = {"query": RunnablePassthrough()} | prompt | llm_with_tool

# 5.调用链应用，并获取输出响应
query = "上海现在天气怎样，并且请用谷歌搜索工具查询一下2024年巴黎奥运会中国代表团共获得几枚金牌？"
resp = chain.invoke(query)

# 6.判断是工具调用还是正常输出结果
# 处理可能的工具调用
try:
    # 尝试获取工具调用
    if hasattr(resp, 'tool_calls'):
        tool_calls = resp.tool_calls
    else:
        # 检查是否有其他格式的工具调用
        tool_calls = []
        if hasattr(resp, 'additional_kwargs') and 'tool_calls' in resp.additional_kwargs:
            tool_calls = resp.additional_kwargs.get('tool_calls', [])
except:
    tool_calls = []

if not tool_calls or len(tool_calls) <= 0:
    print("生成内容: ", resp.content)
else:
    # 7.将历史的系统消息、人类消息、AI消息组合
    messages = prompt.invoke(query).to_messages()
    messages.append(resp)

    # 8.循环遍历所有工具调用信息
    for tool_call in tool_calls:
        # 处理不同格式的工具调用
        if isinstance(tool_call, dict):
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args")
            tool_call_id = tool_call.get("id")
        else:
            # 如果是ToolCall对象
            tool_name = tool_call.name
            tool_args = tool_call.get("args")
            tool_call_id = tool_call.get("id")

        tool = tool_dict.get(tool_name)  # 获取需要执行的工具
        if tool:
            print("正在执行工具: ", tool.name)
            content = tool.invoke(tool_args)  # 工具执行的内容/结果
            print("工具返回结果: ", content)
            messages.append(ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            ))
        else:
            print(f"工具 {tool_name} 未找到")

    # 将工具结果发送回模型
    final_response = llm.invoke(messages)
    print("输出内容: ", final_response.content)
