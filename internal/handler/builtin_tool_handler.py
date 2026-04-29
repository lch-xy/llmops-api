#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/29 20:06
@Author  : LCH
@File   : builtin_tool_handler.py
"""
import io

from flask import send_file

from internal.service.builtin_tool_service import BuiltinToolService
from pkg.response import success_json


class BuiltinToolHandler:
    """内置工具 API 接口处理器"""

    builtin_tool_service: BuiltinToolService

    def get_builtin_tools(self):
        builtin_tools = self.builtin_tool_service.get_builtin_tools()
        return success_json(builtin_tools)

    def get_provider_tool(self, provider_name: str, tool_name: str):
        builtin_tool = self.builtin_tool_service.get_provider_tool(provider_name, tool_name)
        return success_json(builtin_tool)

    def get_provider_icon(self, provider_name: str):
        # send_file 会告诉浏览器这是一张图片，浏览器就会直接显示出 SVG
        icon_bytes, mimetype = self.builtin_tool_service.get_provider_icon(provider_name)
        return send_file(io.BytesIO(icon_bytes), mimetype=mimetype)

    def get_categories(self):
        categories = self.builtin_tool_service.get_categories()
        return success_json(categories)
