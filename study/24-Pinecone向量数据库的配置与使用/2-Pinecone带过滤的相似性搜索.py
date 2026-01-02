#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/2 13:52
@Author  : LCH
@File   : 2-Pinecone带过滤的相似性搜索.py
"""

import dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()

embedding = OllamaEmbeddings(model="embeddinggemma")

db = PineconeVectorStore(index_name="llmops", embedding=embedding, namespace="dataset")

query = "我养了一只猫，叫笨笨"
print(db.similarity_search_with_relevance_scores(
    query,
    # filter={"$or": [{"page": 5}, {"account_id": 1}]}
    filter={"page": {"$gte": 5}}
))
