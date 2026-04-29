#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/29 16:37
@Author  : LCH
@File   : builtin_tool_service.py
"""
from dataclasses import dataclass

from injector import inject

from internal.core.tools.builtin_tools.categories.builtin_category_manager import BuiltinCategoryManager
from internal.core.tools.builtin_tools.providers.builtin_provider_manager import BuiltinProviderManager
from internal.exception import NotFoundException


@inject
@dataclass
class BuiltinToolService:
    """内置工具业务逻辑层"""

    # 依赖注入：只要加上这两个声明，系统会自动把我们前面写好的那两个单例大管家送过来！
    builtin_provider_manager: BuiltinProviderManager
    builtin_category_manager: BuiltinCategoryManager

    def __init__(self, tool_yaml_path):
        self.tool_yaml_path = tool_yaml_path

    def get_builtin_tools(self) -> list[dict]:
        """获取所有厂商及名下的工具，拼装成前端需要的树状结构"""
        # 1. 直接问管家拿所有厂商
        providers = self.builtin_provider_manager.get_providers()

        builtin_tools = []
        for provider in providers:
            # 2. 把厂商的皮肤（provider_entity）转成字典
            provider_dict = provider.provider_entity.model_dump()
            # 3. 再加上它名下的所有工具
            provider_dict["tools"] = [
                tool.model_dump() for tool in provider.get_tool_entities()
            ]
            builtin_tools.append(provider_dict)

        return builtin_tools

    def get_provider_tool(self, provider_name: str, tool_name: str) -> dict:
        """获取某个具体工具的详细参数"""
        provider = self.builtin_provider_manager.get_provider(provider_name)
        if not provider:
            raise NotFoundException("该内置提供商不存在")

        tool_entity = provider.get_tool_entity(tool_name)
        if not tool_entity:
            raise NotFoundException("该提供商下不存在该工具")

        # 获取工具的 params 列表（之前在 yaml 里写的那些参数），
        # 前端拿到这个 params 数组后，就能自动渲染出一个填表单的界面（比如：搜索框）
        return tool_entity.model_dump()

    def get_provider_icon(self, provider_name: str) -> tuple[bytes, str]:
        """给前端返回厂商的 SVG 图标"""
        provider = self.builtin_provider_manager.get_provider(provider_name)
        if not provider:
            raise NotFoundException("该提供商不存在")
        # 拿着厂商的 category 去分类管家里找对应的 svg 代码
        category = self.builtin_category_manager.get_category_map().get(provider.provider_entity.category)
        icon_str = category.get("icon")

        return icon_str.encode("utf-8"), "image/svg+xml"

    def get_categories(self) -> list[dict]:
        """获取所有分类列表"""
        category_map = self.builtin_category_manager.get_category_map()
        return [item.get("entity").model_dump() for item in category_map.values()]
