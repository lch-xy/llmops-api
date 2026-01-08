#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/8 19:29
@Author  : LCH
@File   : 3-URL网页加载器.py
"""
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://tech.meituan.com/2025/12/05/ai-coding-unit-testing.html")
documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
