#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/14 19:36
@Author  : LCH
@File   : 2-as_retriever检索器示例.py
"""
import os

import dotenv
import weaviate
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1.构建加载器与分割器
loader = UnstructuredMarkdownLoader("./项目API文档.md")
text_splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n\n",
        "\n",
        r"[。！？]",
        r"[.!?]\s",
        r"[；;]\s?",
        r"[，,]\s?",
        " ",
    ],
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

# 2.加载文档并分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)

# 3.将数据存储到向量数据库
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ),
    index_name="Dataset",
    text_key="text",
    embedding=OllamaEmbeddings(model="embeddinggemma"),
)
db.add_documents(chunks)

# 4.转换检索器（带阈值的相似性搜索，数据为10条，得分阈值为0.5）
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 10,
        "score_threshold": 0.5
    },
)

# 5.检索结果
documents = retriever.invoke("关于配置接口的信息有哪些")

print(list(document.page_content[:50] for document in documents))
print(len(documents))

db._client.close()
