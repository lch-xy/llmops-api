# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/11 17:50
@Author  : LCH
@File   : 2-LLM文生图应用.py
"""
import os

import dotenv
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

dalle = OpenAIDALLEImageGenerationTool(api_wrapper=DallEAPIWrapper(model="dall-e-3"))

llm = ChatOpenAI(
    model="qwen3.5:9b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)
llm_with_tools = llm.bind_tools([dalle], tool_choice="openai_dalle")

chain = llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | dalle

print(chain.invoke("帮我绘制一张老爷爷爬山的图片"))
