#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/2 09:50
@Author  : LCH
@File   : 1-Hugging Face本地嵌入模型.py
"""
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L12-v2",
    cache_folder="./embeddings/"
)

query_vector = embeddings.embed_query("你好，是张三，我喜欢吹牛逼")

print(query_vector)
print(len(query_vector))
