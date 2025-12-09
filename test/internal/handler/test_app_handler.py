#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/8 20:17
@Author  : LCH
@File   : test_app_handler.py
"""
import pytest

from pkg.response import HttpCode


class TestAppHandler:
    """测试应用控制器"""

    @pytest.mark.parametrize("query", [None, "你好"])
    def test_completion(self, query, client):
        """测试聊天接口"""
        resp = client.post("/app/completion", json={"query": query})
        assert resp.status_code == 200
        if query is None:
            assert resp.json.get("code") == HttpCode.VALIDATE_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS
        print("响应内容", resp.json)
