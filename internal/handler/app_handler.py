# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 19:31
@Author  : LCH
@File   : app_handler.py
"""
import os

from flask import request
from openai import OpenAI

from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from pkg.response import success_json, validate_error_json


class AppHandler:
    """应用控制器"""

    def completion(self):
        """聊天接口"""
        # 1.提取从接口中获取的输入
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)
        query = request.json.get("query")

        # 2.构建OpenAi客户端，并发起请求
        client = OpenAI(
            ## OPENAI_API_BASE_URL 不会读取到要单独传
            base_url=os.getenv("OPENAI_API_BASE_URL")
        )
        # 3.得到请求响应，然后讲OpenAi的响应传递给前端
        completion = client.chat.completions.create(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": "你是聊天机器人，请根据用户的输入回复对应的信息"},
                {"role": "user", "content": query},
            ]
        )
        content = completion.choices[0].message.content

        return success_json({"content": content})

    def ping(self):
        raise FailException("数据未找到")
        return {"ping": "pong"}
