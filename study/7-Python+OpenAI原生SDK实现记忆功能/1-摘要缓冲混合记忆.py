#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/18 17:46
@Author  : LCH
@File   : 1-摘要缓冲混合记忆.py
"""
import os
from typing import Any

import dotenv
from openai import OpenAI

dotenv.load_dotenv()


# 1.max_token用于判断是否需要生成摘要
# 2.summary存储摘要信息
# 3.chat_history存储聊天记录
# 4.get_num_tokens用于判断是否需要生成摘要
# 5.save_content用于存储新的聊天记录
# 6.get_buffer_string用于将历史对话转成字符串
# 7.load_memory_variable用于加载记忆变量信息
# 8.summary_text用于将旧摘要和传入的对话生成新的摘要
class ConversionSummaryBuuferMemory:
    """摘要缓冲混合记忆"""

    def __init__(self, summary: str, chat_history: list = None, max_tokens: int = 300):
        self.summary = summary
        self.chat_history = [] if chat_history is None else chat_history
        self.max_tokens = max_tokens
        self._client = OpenAI(base_url=os.getenv("OPENAI_API_BASE_URL"))

    @classmethod
    def get_num_tokens(cls, query: str) -> int:
        """获取文本的token数量"""
        return len(query)

    def save_content(self, human_query: str, ai_content: str):
        """保存新的聊天记录"""
        self.chat_history.append({"human": human_query, "ai": ai_content})

        buffer_string = self.get_buffer_string()

        tokens = self.get_num_tokens(buffer_string)

        if tokens > self.max_tokens:
            # 1.生成摘要
            # 2.将生成的摘要和传入的查询语句拼接成新的摘要
            # 3.将新的摘要保存到summary中
            first_chat = self.chat_history[0]
            print("生成摘要中。。。。。。")
            self.summary = self.summary_text(self.summary,
                                             f"Human:{first_chat.get('human')}\nAI:{first_chat.get('ai')}")
            print("生成成功:", self.summary)
            del self.chat_history[0]

    def get_buffer_string(self) -> str:
        """将历史对话转成字符串"""
        buffert: str = ""
        for chat in self.chat_history:
            buffert += f"Human:{chat.get('human')}\nAI:{chat.get('ai')}\n"
        return buffert.strip()

    def load_memory_variable(self) -> dict[str, Any]:
        """加载记忆变量信息"""
        buffer_string = self.get_buffer_string()
        return {"chat_history": f"摘要:{self.summary}n\n历史信:{buffer_string}"}

    def summary_text(self, origin_summary: str, new_line: str) -> str:
        """用于将旧摘要和传入的新对话生成一个新摘要"""
        prompt = f"""你是一个强大的聊天机器人，请根据用户提供的谈话内容，总结摘要，并将其添加到先前提供的摘要中，返回一个新的摘要，除了新摘要其他任何数据都不要生成，如果用户的对话信息里有一些关键的信息，比方说姓名、爱好、性别、重要事件等等，这些全部都要包括在生成的摘要中，摘要尽可能要还原用户的对话记录。

            请不要将<example>标签里的数据当成实际的数据，这里的数据只是一个示例数据，告诉你该如何生成新摘要。
        
            <example>
            当前摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量。
        
            新的对话：
            Human：为什么你认为人工智能是一股向善的力量？
            AI：因为人工智能会帮助人类充分发挥潜力。
        
            新摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量，因为它将帮助人类充分发挥潜力。
            </example>
        
            =====================以下的数据是实际需要处理的数据=====================
        
            当前摘要：{origin_summary}
        
            新的对话：
            {new_line}
        
            请帮用户将上面的信息生成新摘要。"""
        completion = self._client.chat.completions.create(
            model="qwen3:8b",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content


client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE_URL")
)
memory = ConversionSummaryBuuferMemory("", [], 300)

while True:
    query = input("human：")

    if query == "q":
        break

    memory_variable = memory.load_memory_variable()
    answer_prompt = (
        "你是一个强大聊天机器人，请根据对应的上下文和用户提问解决问题。\n\n"
        f"{memory_variable.get('chat_history')}\n\n"
        f"用户的提问是：{query}"
    )

    responses = client.chat.completions.create(
        model="qwen3:8b",
        messages=[
            {"role": "user", "content": answer_prompt}
        ],
        stream=True
    )

    print("AI：", end="", flush=True)
    ai_content = ""
    for chunk in responses:
        content = chunk.choices[0].delta.content
        if content is None:
            break
        ai_content += content
        print(content, flush=True, end="")
    print("")
    memory.save_content(query, ai_content)
