#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第06讲 合规爬虫：抓取 books.toscrape.com 前 3 页，输出 items.csv。

合规要点：
  1. 先读取 robots.txt；404 视为「站点未声明限制」，仍按自律规则抓取。
  2. 自定义 UA（EDU-Crawler/1.0），timeout=10，Retry(total=3, backoff=0.5, 429/5xx)。
  3. 只抓 3 页、只发 GET、页间隔 1 秒，按 URL 去重。
  4. 仅用于课程实验，不转载、不商用、不访问站内搜索/登录等非公开页面。
"""
import csv
import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin
from urllib3.util.retry import Retry

BASE = "https://books.toscrape.com/"
UA = "EDU-Crawler/1.0 (course lab; contact: student@example.edu)"
MAX_PAGES = 3
INTERVAL = 1.0
FIELDS = ["title", "price", "rating", "url"]


def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    retry = Retry(total=3, backoff_factor=0.5,
                  status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["GET"])
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


def check_robots(session):
    try:
        r = session.get(BASE + "robots.txt", timeout=10)
        print("[robots] HTTP %s -> %s" % (r.status_code, "有声明" if r.status_code == 200 else "无声明(404)，按允许处理"))
        if r.status_code == 200:
            print(r.text[:500])
    except Exception as e:
        print("[robots] 读取失败：%s，按无声明处理" % e)


def parse_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for pod in soup.select("article.product_pod"):
        title = pod.select_one("h3 a").get("title", "") or pod.select_one("h3 a").get_text(strip=True)
        price = pod.select_one("p.price_color").get_text(strip=True)
        rating_cls = pod.select_one("p.star-rating").get("class", [])
        rating = next((c.replace("star-rating", "").strip() for c in rating_cls if c != "star-rating"), "")
        href = pod.select_one("h3 a").get("href", "")
        # 相对链接转绝对链接
        if href.startswith("../"):
            url = "https://books.toscrape.com/catalogue/" + href[3:]
        elif href.startswith("catalogue/"):
            url = BASE + href
        else:
            url = BASE + "catalogue/" + href
        out.append({"title": title, "price": price, "rating": rating, "url": url})
    return out


def main():
    session = make_session()
    check_robots(session)

    seen = set()
    rows = []
    url = BASE + "index.html"
    for page in range(1, MAX_PAGES + 1):
        r = session.get(url, timeout=10)
        r.raise_for_status()
        print("[page %d] %s -> HTTP %s, %d bytes" % (page, url, r.status_code, len(r.content)))
        new = 0
        for item in parse_page(r.text, url):
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            rows.append(item)
            new += 1
        print("          新增 %d 条，累计 %d 条" % (new, len(rows)))

        soup = BeautifulSoup(r.text, "html.parser")
        nxt = soup.select_one("li.next a")
        if not nxt:
            break
        href = nxt.get("href", "")
        url = urljoin(url, href)
        print("          下一页 -> %s" % url)
        time.sleep(INTERVAL)

    with open("items.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("[done] 写入 items.csv：表头 + %d 行，重复 %d 条" % (len(rows), len(seen) - len(rows)))

    # 供报告核对的搜索统计
    for kw in ["art", "the", "travel"]:
        n = sum(1 for x in rows if kw in x["title"].lower())
        print("[stat] q=%-7s -> %d 条" % (kw, n))


if __name__ == "__main__":
    main()
