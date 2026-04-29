#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/28 10:57
@Author  : LCH
@File   : builtin_category_manager.py
"""
import os
from typing import Any

import yaml
from injector import inject, singleton
from pydantic import BaseModel, Field

from internal.core.tools.builtin_tools.entites.category_entity import CategoryEntity
from internal.exception import NotFoundException


@inject  # 依赖注入标记
@singleton  # 单例模式标记：保证全局只加载一次！
class BuiltinCategoryManager(BaseModel):
    """内置的工具分类管理器"""
    # 不要写 dict[str,Any] = [] or {}  会导致 共享内存（引用传递）
    # default_factory=dict 每次创建一个干净的字典出来
    category_map: dict[str, Any] = Field(default_factory=dict)

    def __int__(self, **kwargs):
        super().__int__(**kwargs)
        self._init_categories()

    def get_category_map(self) -> dict[str, Any]:
        return self.category_map

    def _init_categories(self):
        """核心：去 categories.yaml 里把分类信息和对应的 svg 图片全读进内存"""
        if self.category_map: return

        # 1. 找到 yaml 文件
        category_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(category_path, "categories.yaml"), encoding="utf-8") as f:
            categories = yaml.safe_load(f)

        for category in categories:
            # 2. 生成刚才写的 CategoryEntity
            category_entity = CategoryEntity(**category)
            # 3. 强校验：去 icons 文件夹里找有没有真的放这个 svg 图片
            icon_path = os.path.join(category_path, "icons", category_entity.icon)
            if not os.path.exists(icon_path):
                raise NotFoundException(f"分类 {category_entity.category} 的 icon 未提供")
            # 4. 把 svg 图片代码读出来，一起装进字典
            with open(icon_path, encoding="utf-8") as f:
                self.category_map[category_entity.category] = {
                    "entity": category_entity,
                    "icon": f.read(),
                }
