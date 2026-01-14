#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/14 20:02
@Author  : LCH
@File   : 3-最大边际相关性示例.py
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

# 4.执行最大边际相关性搜索
# search_documents = db.similarity_search("关于应用配置的接口有哪些？")
search_documents = db.max_marginal_relevance_search("关于应用配置的接口有哪些？")

# 5.打印搜索的结果
# print(list(document.page_content[:100] for document in search_documents))
for document in search_documents:
    print(document.page_content[:100])
    print("===========")

db._client.close()
