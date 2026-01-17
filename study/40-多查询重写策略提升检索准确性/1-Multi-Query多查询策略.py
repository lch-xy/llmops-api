#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/17 12:48
@Author  : LCH
@File   : 1-Multi-Query多查询策略.py
"""
import os

import dotenv
import weaviate
from langchain_classic.retrievers import MultiQueryRetriever
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_weaviate import WeaviateVectorStore

dotenv.load_dotenv()

# 1.构建向量数据库检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=os.getenv("WEAVIATE_API_KEY"),
    ),
    index_name="Dataset",
    text_key="text",
    embedding=OllamaEmbeddings(model="embeddinggemma")
)
retriever = db.as_retriever(search_type="mmr")

# 2.创建多查询检索器
multi_query_retriever = MultiQueryRetriever.from_llm(retriever=retriever,
                                                     llm=ChatOpenAI(model="qwen3:8b",
                                                                    base_url=os.getenv("OPENAI_API_BASE_URL"),
                                                                    temperature=0),
                                                     include_original=True)
 
# 3.执行检索
docs = multi_query_retriever.invoke("我的猫咪喜欢干嘛")
print(docs)
print(len(docs))

db._client.close()
