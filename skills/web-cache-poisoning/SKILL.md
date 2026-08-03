---
name: web-cache-poisoning
description: >
  Web Cache Poisoning / Deception testing skill. Use when response headers
  contain X-Cache, X-Varnish, CF-Cache-Status, or when the target uses
  Cloudflare/CloudFront/Varnish. Focuses on poisoning cache with malicious
  X-Forwarded-Host, X-Original-URL, or Host headers to deliver stored XSS
  or open redirects to other users.
---

# Web Cache Poisoning / Deception

## Overview

Web 缓存投毒的核心是利用 **CDN / 反向代理（Varnish、Cloudflare、AWS CloudFront、Nginx）** 对 HTTP 请求头的解析差异，将**恶意响应**存入缓存，分发给其他正常用户。

**两类主要攻击面**：

1. **Header 注入**：`X-Forwarded-Host` / `X-Original-URL` / `Forwarded` 等头被后端用于生成页面链接或重定向，而缓存键未包含这些头。
2. **缓存键污染**：通过 `?cb=` 或 `?v=` 参数绕过缓存，同时利用 `Host` 或 `X-Forwarded-Host` 生成不同内容，导致正常用户的缓存被恶意内容替换。

---

## Quick Start: First-Pass Test (30秒)

### 1. 检测缓存存在性

观察响应头：

```http
X-Cache: hit / miss          # Varnish / Squid
CF-Cache-Status: HIT / MISS  # Cloudflare
X-Varnish: 12345678          # 后端使用 Varnish
Cache-Control: public, max-age=3600