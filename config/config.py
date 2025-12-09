#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 21:54
@Author  : LCH
@File   : config.py
"""
import os
from typing import Any

from config.default_config import DEFAULT_CONFIG


# def 函数名(参数列表) -> 返回值类型:
def _get_env(key: str) -> Any:
    return os.getenv(key, DEFAULT_CONFIG.get(key))


# def 函数名(参数列表) -> 返回值类型:
def _get_bool_env(key: str) -> bool:
    value: str = _get_env(key)
    return value.lower() == "true" if value is not None else False


class Config:
    """配置类"""

    def __init__(self):
        # 关闭wtf的csrf保护
        self.WTF_CSRF_ENABLED = _get_env("WTF_CSRF_ENABLED")

        # 配置数据库
        self.SQLALCHEMY_DATABASE_URI = _get_env("SQLALCHEMY_DATABASE_URI")
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(_get_env("SQLALCHEMY_POOL_SIZE")),
            "pool_recycle": int(_get_env("SQLALCHEMY_POOL_RECYCLE"))
        }
        self.SQLALCHEMY_ECHO = _get_env("SQLALCHEMY_ECHO")
