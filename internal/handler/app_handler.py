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

from injector import inject
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

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

    def completion(self):
        """聊天接口"""
        # 1.提取从接口中获取的输入
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.构建组件
        prompt = ChatPromptTemplate.from_template("{query}")
        llm = ChatOpenAI(
            model="qwen3:8b",
            base_url=os.getenv("OPENAI_API_BASE_URL")
        )
        parser = StrOutputParser()

        # 3.构建链
        chain = prompt | llm | parser

        # 4.调用链得到结果 要用req.query.data
        content = chain.invoke({"query": req.query.data})

        return success_json({"content": content})

    def ping(self):
        raise FailException("数据未找到")
        return {"ping": "pong"}
