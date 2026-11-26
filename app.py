#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第06讲 Flask 展示：读取 items.csv，渲染列表并提供不区分大小写的搜索。

启动：python app.py  然后浏览器访问 http://127.0.0.1:5000/
安全：Jinja2 默认对变量自动转义，搜索词原样回填输入框也不会造成 XSS。
"""
import csv
import os
from flask import Flask, render_template, request

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "items.csv")


def load_items():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    items = load_items()
    if q:
        # 不区分大小写，匹配书名；搜索词不做任何 HTML 拼接，交给模板转义
        items = [x for x in items if q.lower() in x["title"].lower()]
    return render_template("index.html", items=items, q=q, total=len(items))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
