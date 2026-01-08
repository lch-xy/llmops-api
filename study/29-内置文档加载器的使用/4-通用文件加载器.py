#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/8 19:29
@Author  : LCH
@File   : 4-通用文件加载器.py.py
"""
from langchain_community.document_loaders import UnstructuredFileLoader

loader = UnstructuredFileLoader("./项目API资料.md")

documents = loader.load()

print(documents)
print(type(documents))
print(documents[0].metadata)
