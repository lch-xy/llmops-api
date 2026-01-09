#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/8 20:20
@Author  : LCH
@File   : 2-FileSystemBlobLoader示例.py
"""
from langchain_community.document_loaders import FileSystemBlobLoader

loader = FileSystemBlobLoader("./喵喵.txt", show_progress=True)

for blob in loader.yield_blobs():
    print(blob.as_string())
