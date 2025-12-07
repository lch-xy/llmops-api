#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 19:52
@Author  : LCH
@File   : http.py
"""
from flask import Flask

from config import Config
from internal.router import Router


class Http(Flask):
    """HTTP服务"""

    ## args:非命名参数 kwargs:命名参数
    def __init__(self, *args, conf: Config, router: Router, **kwargs):
        super().__init__(*args, **kwargs)

        ## 注册应用路由
        router.regiter_router(self)

        # 调用Flask的方法 将配置应用到Flask中
        self.config.from_object(conf)
