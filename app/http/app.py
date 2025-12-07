#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/7 19:59
@Author  : LCH
@File   : app.py
"""
from injector import Injector

from internal.router import Router
from internal.service.http import Http

injector = Injector()
app = Http(__name__, router=injector.get(Router))

if __name__ == "__main__":
    app.run(debug=True)
