#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 19:52
@Author  : LCH
@File   : http.py
"""
import os

from flask import Flask

from config import Config
from internal.exception import CustomException
from internal.model.app import App
from internal.router import Router
from pkg.response import json, Response, HttpCode
from pkg.sqlalchemy import SQLAlchemy


class Http(Flask):
    """HTTP服务"""

    ## args:非命名参数 kwargs:命名参数
    def __init__(self, *args, conf: Config, db: SQLAlchemy, router: Router, **kwargs):
        # 调用父类构造函数初始化
        super().__init__(*args, **kwargs)

        # 调用Flask的方法 将配置应用到Flask中
        self.config.from_object(conf)

        # 注册绑定异常错误处理
        self.register_error_handler(Exception, self._register_error_handler)

        # 初始化db
        db.init_app(self)
        with self.app_context():
            _ = App()
            db.create_all()

        # 注册应用路由
        router.regiter_router(self)

    def _register_error_handler(self, error: Exception):
        # 1.异常信息是否为自定义异常
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data is not None else {}
            ))

        # 2.如果不是自定义异常，则有可能是程序 数据库的异常，也可以提取信息 str()将异常转成字符串
        if self.debug or os.getenv("FLASK_ENV") == "development":
            return error
        else:
            return json(Response(
                code=HttpCode.FAIL,
                message=str(error),
                data={}
            ))
