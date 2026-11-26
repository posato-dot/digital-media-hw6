# 数字媒体程序基础第六次作业

## 第06讲 网络爬虫与网页服务器 · 抓取 → CSV → Flask 展示

本仓库包含第 06 讲的全部提交物（按要求不含 PPT）：合规爬虫源码、真实抓取的数据、Flask 展示应用与模板、合规说明，以及实验报告 PDF。

## 文件清单

| 文件 | 说明 |
|---|---|
| `crawler.py` | 合规爬虫：robots 探测、自定义 UA、timeout=10、Retry(3, 0.5)、只 GET、1s 间隔、URL 去重、抓取 3 页 |
| `items.csv` | 真实抓取结果：表头 + 60 行，字段 `title/price/rating/url`，UTF-8 带 BOM |
| `app.py` | Flask 应用：读取 CSV 渲染列表，支持不区分大小写搜索、匹配计数与空结果提示 |
| `templates/index.html` | Jinja2 模板，变量自动转义，防 XSS |
| `合规说明.md` | 抓取范围、robots 处理、频率与自律、数据用途、Web 安全、复现命令 |
| `第06讲_实验报告.pdf` | 填好的实验报告（5 页） |

## 实测结果

- 目标站 `https://books.toscrape.com/`（公开爬虫练习站），`robots.txt` 返回 404，按「未声明限制」处理但保持自律。
- 抓取 3 页（index + page-2 + page-3），每页 20 条，累计 60 条，URL 去重后重复 0 条。
- Flask 实测：`GET /` 返回 200 并显示 60 行；`?q=art` 5 条、`?q=the` 24 条、`?q=travel` 0 条（显示空结果提示）；`?q=<script>alert(1)</script>` 被转义为文本，XSS 防护生效。
- 服务器日志全部 200，无 403/429。

## 复现

```bash
pip install requests beautifulsoup4 flask
python crawler.py   # 重新抓取并生成 items.csv
python app.py       # http://127.0.0.1:5000/
```
