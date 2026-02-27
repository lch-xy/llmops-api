#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/2/27 10:21
@Author  : LCH
@File   : 2-小文档块检索大文档块.py
"""

from os import getenv

import dotenv
import weaviate
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import LocalFileStore
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1.创建加载器与文档列表，并加载文档
loaders = [
    UnstructuredFileLoader("./电商产品数据.txt"),
    UnstructuredFileLoader("./项目API文档.md"),
]
docs = []
for loader in loaders:
    docs.extend(loader.load())

# 2.创建文本分割器
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

# 3.创建向量数据库与文档数据库
vector_store = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url=getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(getenv("WEAVIATE_API_KEY")),
    ),
    index_name="ParentDocument",
    text_key="text",
    embedding=OllamaEmbeddings(model="embeddinggemma"),
)
byte_store = LocalFileStore("./parent-document")

# 4.创建父文档检索器
retriever = ParentDocumentRetriever(
    vectorstore=vector_store,
    byte_store=byte_store,
    child_splitter=text_splitter,
    parent_splitter=parent_splitter,
)

# 5.添加文档
retriever.add_documents(docs, ids=None)

# 6.检索并返回内容
search_docs = retriever.vectorstore.similarity_search("分享关于LLMOps的一些应用配置")
# search_docs = retriever.invoke("分享关于LLMOps的一些应用配置")
print(search_docs)
print(len(search_docs))

vector_store._client.close()
