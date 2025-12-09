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
        bp.add_url_rule("ping", view_func=self.app_handler.ping)
        bp.add_url_rule("/app/completion", methods=["POST"], view_func=self.app_handler.completion)
        bp.add_url_rule("/app", methods=["POST"], view_func=self.app_handler.create_app)
        bp.add_url_rule("/app/<uuid:id>", methods=["GET"], view_func=self.app_handler.get_app)
        bp.add_url_rule("/app/<uuid:id>", methods=["PUT"], view_func=self.app_handler.update_app)
        bp.add_url_rule("/app/<uuid:id>", methods=["DELETE"], view_func=self.app_handler.delete_app)

        ## 3.在应用上去注册蓝图
        app.register_blueprint(bp)
