#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/14 20:06
@Author  : LCH
@File   : 1-向量数据库检索与Runnable使用技巧.py
"""
import os

import dotenv
import weaviate
from langchain_core.runnables import ConfigurableField
from langchain_ollama import OllamaEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1.构建向量数据库
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ),
    index_name="Dataset",
    text_key="text",
    embedding=OllamaEmbeddings(model="embeddinggemma"),
)

# 2.转换检索器
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.5},
).configurable_fields(
    search_type=ConfigurableField(id="db_search_type"),
    search_kwargs=ConfigurableField(id="db_search_kwargs"),
)

# 3.修改运行时配置执行MMR搜索，并返回4条数据
mmr_documents = retriever.with_config(
    configurable={
        "db_search_type": "mmr",
        "db_search_kwargs": {
            "k": 4,
        }
    }
).invoke("关于应用配置的接口有哪些？")
print("相似性搜索: ", mmr_documents)
print("内容长度:", len(mmr_documents))

print(mmr_documents[0].page_content[:20])
print(mmr_documents[1].page_content[:20])

db._client.close()
