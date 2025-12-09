#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/9 10:55
@Author  : LCH
@File   : conftest.py
"""

import pytest

from app.http.app import app


@pytest.fixture
def client():
    """获取Flask应用的测试应用，并返回"""
    app.config["TESTING"] = True
    with app.test_client() as client:  # Flask 提供的 HTTP 模拟客户端
        # yield 的作用：
        # 	•	yield 之前：准备测试资源
        # 	•	yield 返回的对象 → 注入给测试函数
        # 	•	测试执行完后 → 自动执行 with 里的清理逻辑
        yield client
