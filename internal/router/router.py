#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 19:34
@Author  : LCH
@File   : router.py
"""
from dataclasses import dataclass

from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler


@inject  ## 这是小写
@dataclass  ## 自动注入
class Router:
    """路由控制器"""

    app_handler: AppHandler

    def regiter_router(self, app: Flask):
        """注册路由"""

        ## 1.创建蓝图
        bp = Blueprint("llmops", __name__, url_prefix="")

        ## 2.将url与控制器方法做绑定
        app_handler = AppHandler()
        # bp.add_url_rule("ping", methods=["GET", "POST", "DELETE"])
        bp.add_url_rule("ping", view_func=self.app_handler.ping)

        ## 3.在应用上去注册蓝图
        app.register_blueprint(bp)
