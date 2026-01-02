#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/2 13:53
@Author  : LCH
@File   : 3-删除指定数据.py
"""

import dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()

embedding = OllamaEmbeddings(model="embeddinggemma")

db = PineconeVectorStore(index_name="llmops", embedding=embedding, namespace="dataset")

id = "af548cd7-dd8f-41c6-aeeb-144b60ff4d44"
db.delete([id], namespace="dataset")

# pinecone_index = db.get_pinecone_index("llmops")
# pinecone_index.update(id="xxx", values=[], metadata={}, namespace="dataset")
