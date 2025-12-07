#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 21:54
@Author  : LCH
@File   : config.py
"""


class Config:
    """配置类"""

    def __init__(self):
        # 关闭wtf的csrf保护
        self.WTF_CSRF_ENABLED = False
