#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/9 15:13
@Author  : LCH
@File   : module.py
"""
from flask_sqlalchemy import SQLAlchemy
from injector import Module, Binder

from internal.extension.database_extension import db


# 类似Spring 的 @Configuration 类
class ExtensionModule(Module):
    # 扩展模块依赖注入
    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)
