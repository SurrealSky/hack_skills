---
name: nosql-injection
description: >
  NoSQL Injection testing skill for MongoDB-based endpoints. Use when
  URL parameters, JSON bodies, or query fields contain operators like `$ne`,
  `$gt`, `$regex`, `$where`, or when classic SQLi payloads fail but
  authentication/authorization bypass is suspected. Focuses on MongoDB
  operator injection and JavaScript execution.
---

# NoSQL Injection (MongoDB)

## Overview

NoSQL 注入通常发生在 **MongoDB + Node.js (Express)** 或 **PHP + MongoDB** 环境中。与 SQL 注入不同，MongoDB 使用 JSON 风格的查询对象，攻击核心在于：

1. **操作符注入**：向查询对象中注入 `$ne`（不等于）、`$gt`（大于）、`$regex`（正则）等操作符，绕过登录验证或提取数据。
2. **语法注入**：利用数组或对象破坏查询结构，导致数据泄露。
3. **JavaScript 执行**：利用 `$where` 或 `mapReduce` 执行任意 JS 代码（高风险）。

## When to Use

- 登录/注册接口使用 JSON 请求体（如 `{"username":"admin","password":"123"}`）。
- 搜索/过滤接口使用 URL 参数（如 `?search=admin`）或 JSON 条件。
- 使用 `'` 或 `"` 测试未触发 SQL 错误，但响应行为异常（如返回所有用户）。
- API 文档或报错信息中出现 `MongoError`、`CastError`、`$regex` 等关键字。

---

## Quick Start: First-Pass Test (30秒)

### 1. 登录绕过（最优先）

在登录请求体的 `username` 或 `password` 字段插入数组语法：

```http
POST /api/login
Content-Type: application/json

{"username": "admin", "password": {"$ne": "wrong"}}