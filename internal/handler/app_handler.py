# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 19:31
@Author  : LCH
@File   : app_handler.py
"""
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter

from injector import inject
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import success_json, validate_error_json, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""

    app_service: AppService

    def create_app(self):
        app = self.app_service.create_app()
        return success_message(f"创建成功,id为{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"查询成功,名称为{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"更新成功,名称为{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"删除成功,id为{app.id}")

    def debug(self, app_id: uuid.UUID):
        """聊天接口"""
        # 1.提取从接口中获取的输入
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.创建prompt和记忆
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个强大的聊天助手，能根据用户的提问回复问题"),
            MessagesPlaceholder("history"),
            ("human", "{query}")
        ])

        memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="history",
            return_messages=True,
            input_key="query",
            output_key="output",
            chat_memory=FileChatMessageHistory(
                "./storage/memory/chat_history.txt"
            )
        )

        # 3.创建大语言模型
        llm = ChatOpenAI(
            model="qwen3:8b",
            base_url=os.getenv("OPENAI_API_BASE_URL")
        )

        # 4.创建链应用
        chain = RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        ) | prompt | llm | StrOutputParser()

        # 5.调用链获取响应内容
        chain_input = {"query": req.query.data}
        content = chain.invoke(chain_input)

        # 6.将结果储存到存储中
        memory.save_context(chain_input, {"output": content})

        return success_json({"content": content})

    def ping(self):
        raise FailException("数据未找到")
        return {"ping": "pong"}
