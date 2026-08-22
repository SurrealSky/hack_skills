#!/usr/bin/env python3
"""
recon.py — Windows 本地被动侦察助手（CLAUDE.md 模式 B）

用法:
  py -3 tools/recon.py "https://target.com"            # ROE-PASSIVE：crt.sh 子域 + 静态文件 + JS 挖掘
  py -3 tools/recon.py "https://target.com" --probe    # 追加 ROE-HYBRID：.git/.env/backup 已知路径点测
  py -3 tools/recon.py "https://target.com" --js       # 只做 JS 抓取 + 端点/密钥线索

约束（继承 CLAUDE.md 全局约束，本脚本不越权）:
  - 仅 GET，无写操作、无并发爆破、无危险 payload。
  - 每个路径只请求 1 次（固定小清单），非 wordlist、非 fuzz。
  - --probe 为 ROE-HYBRID 已知路径点测，路径数固定且 ≤ 清单长度。
  - 「每端点 ≤5」计数由调用方 Agent 照常更新 ./temp/rate-counter.md；本脚本单发不重复。
"""

import sys
import re
import urllib.parse

import requests

TIMEOUT = 8
UA = "Mozilla/5.0 (recon passive; authorized assessment)"

STATIC_FILES = [
    "/robots.txt", "/sitemap.xml", "/security.txt", "/humans.txt",
    "/crossdomain.xml", "/.well-known/security.txt",
]

# ROE-HYBRID：高价值已知路径点测（固定清单，非 wordlist）
HYBRID_PATHS = [
    "/.git/HEAD", "/.git/config", "/.env", "/.env.bak",
    "/backup.zip", "/dump.sql",
]

SECRET_RE = re.compile(
    r"(api[_-]?key|secret|token|passw(?:o)?rd|sk_live_[a-z0-9]+"
    r"|aws_access_key|private[_-]?key)"
    r"[\"'`\s]?[:=][\"'`\s]?[^\"'`\s,;]{6,}",
    re.IGNORECASE,
)


def http_get(session, url):
    """返回 (status, content_type, body) 或 None。"""
    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=False,
                        headers={"User-Agent": UA})
        return r.status_code, r.headers.get("content-type", ""), r.text
    except requests.RequestException:
        return None


def crt_subdomains(domain):
    """crt.sh 被动子域收集（第三方数据源，ROE-PASSIVE 可用，不算目标端点计数）。"""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA})
        if r.status_code != 200:
            return []
        data = r.json()
        names = set()
        for item in data:
            for n in item.get("name_value", "").split("\n"):
                n = n.strip().lstrip("*.")
                if n and n.endswith(domain):
                    names.add(n)
        return sorted(names)
    except (requests.RequestException, ValueError):
        return []


def static_scan(session, base):
    print(f"[*] 静态发现文件 {base}")
    for p in STATIC_FILES:
        res = http_get(session, base + p)
        if res is None:
            print(f"    - {p:28} ERR")
            continue
        status, ctype, body = res
        print(f"    - {p:28} {status}  {ctype or ''}")
        if p == "/robots.txt" and status == 200:
            dis = re.findall(r"^Disallow:\s*(\S+)", body, re.M | re.I)
            if dis:
                print(f"        Disallow: {', '.join(dis[:20])}")
        elif p == "/sitemap.xml" and status == 200:
            urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
            if urls:
                print(f"        sitemap URLs: {len(urls)} 条，示例: {', '.join(urls[:8])}")


def hybrid_probe(session, base):
    print(f"[*] 已知路径点测（ROE-HYBRID，固定 {len(HYBRID_PATHS)} 个）")
    for p in HYBRID_PATHS:
        res = http_get(session, base + p)
        if res is None:
            print(f"    - {p:24} ERR")
            continue
        status, ctype, body = res
        mark = "  <-- 疑似泄露" if status == 200 else ""
        print(f"    - {p:24} {status}{mark}")
        if status == 200 and p == "/.git/HEAD":
            print(f"        content: {body.strip()[:60]}")


def js_scan(session, base, js_urls):
    print("[*] JS 挖掘（端点 + 密钥线索）")
    for u in js_urls:
        res = http_get(session, u)
        if res is None:
            print(f"    - {u}  ERR")
            continue
        status, ctype, body = res
        if status != 200:
            print(f"    - {u}  {status}")
            continue
        endpoints = set(re.findall(r"[\"'`](/[a-zA-Z0-9_\-./]{2,})[\"'`]", body))
        secrets = set(m.group(0)[:60] for m in SECRET_RE.finditer(body))
        print(f"    - {u}  端点 {len(endpoints)} / 密钥线索 {len(secrets)}")
        if endpoints:
            print(f"        端点示例: {', '.join(sorted(endpoints)[:10])}")
        if secrets:
            print(f"        密钥线索: {', '.join(sorted(secrets)[:5])}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    target = sys.argv[1].strip()
    probe = "--probe" in sys.argv
    only_js = "--js" in sys.argv

    if "://" not in target:
        target = "https://" + target
    base = target.rstrip("/")
    host = urllib.parse.urlparse(base).netloc

    s = requests.Session()

    if not only_js:
        subs = crt_subdomains(host)
        print(f"[*] crt.sh 子域（{host}）：{len(subs)} 条")
        if subs:
            print("    " + ", ".join(subs[:30]))
        static_scan(s, base)
        if probe:
            hybrid_probe(s, base)

    # 抓主页 + 其 <script src> 引用的 JS
    js_urls = [base]
    res = http_get(s, base)
    if res and res[0] == 200:
        body = res[2]
        for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', body, re.I):
            js_urls.append(urllib.parse.urljoin(base, src))
    js_scan(s, base, js_urls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
