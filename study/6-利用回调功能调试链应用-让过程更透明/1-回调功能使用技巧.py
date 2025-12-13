#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/13 21:52
@Author  : LCH
@File   : 1-回调功能使用技巧.py
"""

import os
import time
from typing import Any
from uuid import UUID

import dotenv
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import LLMResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class LLMOpsCallbackHandler(BaseCallbackHandler):
    """自定义回调处理"""

    start_time: float = 0

    def on_chat_model_start(
            self,
            serialized: dict[str, Any],
            messages: list[list[BaseMessage]],
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            tags: list[str] | None = None,
            metadata: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> Any:
        print(f"开始执行任务：{serialized}")
        print(f"输入：{messages}")
        self.start_time = time.time()

        # def on_llm_new_token(

    #         self,
    #         token: str,
    #         *,
    #         chunk: GenerationChunk | ChatGenerationChunk | None = None,
    #         run_id: UUID,
    #         parent_run_id: UUID | None = None,
    #         **kwargs: Any,
    # ) -> Any:
    #     if token:
    #         print(f"输出：{token}")

    def on_llm_end(
            self,
            response: LLMResult,
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            **kwargs: Any,
    ) -> Any:
        print(f"输出：{response}")
        print(f"总耗时：{time.time() - self.start_time}")


# 1,编排prompt
prompt = ChatPromptTemplate.from_template("{query}")

# 2.创建大语言模型
llm = ChatOpenAI(
    model="qwen3:8b",
    base_url=os.getenv("OPENAI_API_BASE_URL")
)

# 3.创建输出解释器
parser = StrOutputParser()

# 4.编排链 RunnableParallel可以拿掉 因为|会自动拼成RunnableParallel
chain = {"query": RunnablePassthrough()} | prompt | llm | parser

# 5.调用链
res = chain.stream(
    "你是谁?",
    config={"callbacks": [StdOutCallbackHandler(), LLMOpsCallbackHandler()]}
)

for chunk in res:
    pass
