#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/28 10:53
@Author  : LCH
@File   : category_entity.py
"""
from pydantic import BaseModel, field_validator

from internal.exception import FailException


class CategoryEntity(BaseModel):
    """分类实体（比如：搜索）"""
    category: str  # 唯一英文标识
    name: str  # 中文名称
    icon: str  # 图标文件名

    # 这句话的意思是：我要在后台设立一个针对 "icon" 字段的专属安检门！
    @field_validator("icon")
    def check_icon_extension(cls, value: str):
        # 这里的 value 就是准备装入 icon 的那个值（比如 "search.png"）

        # 拦截逻辑：只允许 .svg 格式放行
        if not value.endswith(".svg"):
            # 如果是 .png 或 .jpg，直接报警，禁止这个对象被创建出来！
            raise FailException("该分类的icon图标并不是.svg格式")

        # 安检通过，原样放行，数据正式装入对象
        return value
