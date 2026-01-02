#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/2 10:59
@Author  : LCH
@File   : 1-数据的导入与相似性搜索.py
"""
import os

import dotenv
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
dotenv.load_dotenv()

embedding = OllamaEmbeddings(model="embeddinggemma")

db = FAISS.from_texts(
    ["笨笨是一只很喜欢睡觉的猫咪", "我喜欢在夜晚听音乐,这让我感到放松。", "猫咪在窗台上打盹,看起来非常可爱。",
     "学习新技能是每个人都应该追求的目标。", "我最喜欢的食物是意大利面,尤其是番茄酱的那种。",
     "昨晚我做了一个奇怪的梦,梦见自己在太空飞行。", "我的手机突然关机了,让我有些焦虑。",
     "阅读是我每天都会做的事情,我觉得很充实。", "他们一起计划了一次周末的野餐,希望天气能好。",
     "我的狗喜欢追逐球,看起来非常开心。", ], embedding, relevance_score_fn=lambda distance: 1.0 / (1.0 + distance))

print(db.similarity_search_with_score("我养了一只猫,叫笨笨"))
print("==========================")
print(db.similarity_search_with_relevance_scores("我养了一只猫,叫笨笨", 10))
