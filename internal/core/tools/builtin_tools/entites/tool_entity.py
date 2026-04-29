#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/27 17:13
@Author  : LCH
@File   : tool_entity.py
"""
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class ToolParamType(str, Enum):
    """工具参数类型枚举类"""
    STRING = "string"  # 字符串类型
    NUMBER = "number"  # 数字类型
    BOOLEAN = "boolean"  # 布尔类型
    SELECT = "select"  # 下拉选择类型


class ToolParam(BaseModel):
    """工具参数类型"""
    name: str  # 参数的实际名字，例如 'query'
    label: str  # 给前端展示的标签，例如 '搜索关键词'
    type: ToolParamType  # 参数类型，强制使用上面定义的枚举
    required: bool = False  # 是否必填
    default: Optional[Any] = None  # 默认值
    min: Optional[float] = None  # 如果是数字，允许的最小值
    max: Optional[float] = None  # 如果是数字，允许的最大值
    options: list[dict[str, Any]] = Field(default_factory=list)  # 如果是下拉框，提供选项列表


class ToolEntity(BaseModel):
    """工具实体类，存储的信息映射的是：工具名.yaml 里的数据"""
    name: str  # 工具的英文名，例如 'google_search'
    label: str  # 给用户看的中文名，例如 '谷歌搜索'
    description: str  # 这个工具是干嘛用的
    params: list[ToolParam] = Field(default_factory=list)  # 这个工具需要哪些参数（复用了上面的类）
