#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/21 10:20
@Author  : LCH
@File   : 2.trim_messages修剪消息.py
"""
import os

import dotenv
from langchain_core.messages import HumanMessage, AIMessage, trim_messages
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

dotenv.load_dotenv()

messages = [
    HumanMessage(content="你好，我叫慕小课，我喜欢游泳打篮球，你喜欢什么呢？"),
    AIMessage([
        {"type": "text", "text": "你好，慕小课！我对很多话题感兴趣，比如探索新知识和帮助解决问题。你最喜欢游泳还是篮球呢？"},
        {
            "type": "text",
            "text": "你好，慕小课！我喜欢探讨各种话题和帮助解答问题。你对游泳和篮球的兴趣很广泛，有没有特别喜欢的运动方式或运动员呢？"
        },
    ]),
    HumanMessage(content="如果我想学习关于天体物理方面的知识，你能给我一些建议么？"),
    AIMessage(
        content="当然可以！你可以从基础的天文学和物理学入手，然后逐步深入到更具体的天体物理领域。阅读相关的书籍，如《宇宙的结构》或《引力的秘密》，也可以关注一些优秀的天体物理学讲座和课程。你对哪个方面最感兴趣？"
    ),
]

llm = ChatOpenAI(
    model="qwen3.5:4b",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    temperature=0
)

# 创建一个虚拟的 LLM 实例，专门用来借用它的 Token 计算规则
token_counter_llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="dummy")

update_messages = trim_messages(
    messages,  # 1. 原始的、完整的消息列表
    max_tokens=130,  # 2. 核心限制：修剪后，剩下的消息总Token数不能超过 80
    token_counter=token_counter_llm,  # 3. 计数器：因为不同模型算Token的方式不同，这里直接把你的大模型对象传进去，让它按这个模型的规则来算Token
    strategy="last",  # 4. 保留策略："first" 通常表示保留“最前面的”消息（砍掉后面的）。注：更常见的其实是 "last"（保留最新的对话，砍掉最老的）。这里演示的是保留开头的策略。
    end_on="ai",  # 5. 边界控制：修剪完之后，剩下的列表最后一条消息必须是 "human" 角色。如果不满足，它会继续往前砍，直到最后一条是人类消息。
    allow_partial=False,  # 6. 是否允许"切碎"单条消息：False 代表只能按“整条消息”为单位丢弃。如果设为 True，当某条消息只超了一点点Token时，它会把那条消息的文本切断一部分保留下来。
    text_splitter=RecursiveCharacterTextSplitter(),
    # 7. 文本切分器：配合 allow_partial=True 时使用。告诉程序如果要切碎消息，应该按照什么规则（比如按段落、按标点）来切。这里虽然 allow_partial 是 False，但展示了标准写法。
)

print(update_messages)
