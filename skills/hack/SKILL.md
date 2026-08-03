---
name: hack
description: >
  Entry P0 primary router for HackSkills. Use when the task involves web
  application testing, API security assessment, recon, vulnerability triage,
  exploit path planning, or choosing the right next category skill before any
  deep topic skill.
---

# HACKING SKILLS / HackSkills

## 🧠 内存模式（必须遵守）

本技能采用 **“长驻摘要 + 按需深度”** 混合模式：

1. **长驻上下文（始终保留）**：以下「核心路由表」和「7 条专家直觉」必须始终保留在上下文窗口中，不得卸载。
2. **按需加载（仅在触发时加载）**：当路由表匹配到具体漏洞类别（如 XSS、SSRF、IDOR）时，立即从文件系统加载对应子技能的完整 `SKILL.md` 内容，执行测试；完成该方向测试后，卸载子技能内容，释放上下文窗口给其他模块。
3. **动态重路由**：在每轮子技能执行完毕后，Agent 必须基于新发现（如响应头、报错信息、新增接口）重新对照路由表，判断是否切换到其他攻击面。

---

## 1. 核心路由表（始终驻留）

**使用规则**：先做 Recon（目标类型、身份模型、输入输出位置），再按下表观测到的**现象**匹配最可能的攻击方向，并立即加载对应的子技能。

| 现象 | 优先方向 → 加载子技能路径 |
|---|---|
| 输入反射到 HTML / JS 属性 / DOM 操作 | XSS → `../injection-checking/xss-cross-site-scripting/SKILL.md` |
| 服务端主动访问 URL / 主机名（如头像、预览、Webhook） | SSRF → `../injection-checking/ssrf-server-side-request-forgery/SKILL.md` |
| 接收 XML / Office / SVG / SOAP 请求 | XXE → `../injection-checking/xxe-xml-external-entity/SKILL.md` |
| 路径、文件名、下载接口参数可控（如 `?file=report.pdf`） | Path Traversal / LFI → `../path-traversal-lfi/SKILL.md` |
| API 路径或 JSON 中包含大量对象 ID（如 `/user/123`、`{"org_id": 456}`） | IDOR / BOLA / BFLA → `../auth-sec/idor-broken-object-authorization/SKILL.md` |
| 登录、注册、找回密码、2FA、Session 管理、JWT | Auth Bypass / JWT / OAuth → `../auth-sec/authbypass-authentication-flaws/SKILL.md` 及 `../auth-sec/jwt-oauth-token-attacks/SKILL.md` |
| 多步骤交易、优惠券、价格修改、库存扣减、状态机跳转（如 draft→paid→shipped） | Business Logic → `../business-logic-vuln/business-logic-vulnerabilities/SKILL.md`（同时交叉 Auth Bypass） |
| MongoDB / JSON 查询语法参数（如 `?search[$ne]=1`） | NoSQL Injection → `../injection-checking/nosql-injection/SKILL.md` |
| 命令执行类参数（如 `?ping=8.8.8.8`、`?convert=image.jpg`、导入器） | Command Injection → `../injection-checking/cmdi-command-injection/SKILL.md` |
| HTTP 请求解析异常 / 前后端 CL.TE 或 TE.CL 分帧不一致 / HTTP/2 降级 | Request Smuggling → `../injection-checking/request-smuggling/SKILL.md` |
| Node.js 环境接收 JSON，且包含 `__proto__` 或 `constructor` 关键字 | Prototype Pollution → `../injection-checking/prototype-pollution/SKILL.md` |
| 同名参数重复 / WAF 与后端应用解析顺序不一致 | HTTP Parameter Pollution → `../injection-checking/http-parameter-pollution/SKILL.md` |
| 优惠券领取、密码重置、库存扣减、投票等一次性/限量操作 | Race Condition → `../race-condition/SKILL.md` |
| 文件上传功能 | Insecure File Upload → `../upload-insecure-files/SKILL.md` |
| GraphQL 端点（`/graphql`、`/v1/graphql`） | GraphQL 内省/批量查询 → 先载入 `../api-sec/SKILL.md`，再手动测试内省和别名 |
| 响应头包含 `X-Cache`、`X-Varnish`、`CF-Cache-Status` 且存在 `X-Forwarded-Host` 可控 | Web Cache Poisoning / Deception → 查 `../injection-checking/web-cache-poisoning/SKILL.md`|
| `/robots.txt`、`/sitemap.xml`、`/.well-known/`、`/swagger-ui/`、`/v3/api-docs`、`/graphql` 可访问 | Recon（先爬元数据地图） → 继续使用本技能 Step 1 做信息收集 |
|`/.git/`、`/.env`、`/backup.zip`、`/dump.sql`、`/js/*.js` 中暴露密钥或内部路径 | 信息泄露 → 立即爬取并提取凭证，同时切换到 Auth Bypass / API Security 进行凭证复用测试|
|参数值含 `'` `"` `\` 返回 SQL 错误或响应延时变化|SQLi → `../injection-checking/sqli-sql-injection/SKILL.md`|
|参数值含 `{{` `}}` `${}` `#{` 且响应回显计算值或报模板错误|SSTI → `../injection-checking/ssti-server-side-template-injection/SKILL.md`|
|JSON 请求体中包含非文档字段（如 `role`、`is_admin`、`permission`、`group`）且被接受|Mass Assignment → `../api-sec/SKILL.md`（参考其中 Mass Assignment 章节）|
|响应头包含 `Access-Control-Allow-Origin: *` 或 `null`，且带 `Access-Control-Allow-Credentials: true`| CORS Misconfiguration → `../auth-sec/cors-cross-origin-misconfiguration/SKILL.md`|
<!-- | XML / XSLT 模板处理（如 `?xslt=template.xsl`） | XSLT Injection → `../injection-checking/xslt-injection/SKILL.md` | -->
<!-- | 导出 CSV / Excel 且输出内容部分可控 | CSV Formula Injection → `../injection-checking/csv-formula-injection/SKILL.md` | -->
<!-- | PHP 弱比较参数（如 `?hash=0e123`）或松散类型校验 | Type Juggling → `../injection-checking/type-juggling/SKILL.md` | -->
---

## 2. 推荐测试顺序（始终驻留）

> **优先级自上而下，但允许根据 Recon 结果跳级。**

1. **Recon 与元数据收集**：检查上述路由表最后一行的静态路径、JS 文件、注释、OpenAPI 文档。
2. **API 安全与授权**：IDOR / BOLA / BFLA / Mass Assignment / JWT / OAuth / CORS。
3. **注入类基础**：XSS / SQLi / SSRF / SSTI / XXE（优先测反射型和回显型）。
4. **业务逻辑与竞态**：支付流程、多步骤表单、一次性操作、状态机绕过。
5. **组合链与提权**：将前 4 步中发现的低危问题串联，尝试提升影响。

---

## 3. 7 条专家直觉（始终驻留）

> 这些是基础模型容易忽略、但在真实漏洞赏金中极高价值的思维模式。

1. **同一套过滤逻辑往往复用在多个页面**：找到一个绕过点，立即在所有类似功能点（上传、搜索、导出）中复测。
2. **参数名本身也是攻击面**：WAF 通常紧盯参数值，不盯参数名。尝试添加 `?callback=`、`?debug=`、`?config=` 等非标准参数。
3. **二阶漏洞非常常见**：存储时未过滤不代表读取后进入危险上下文（如 HTML 渲染、JS eval、SQL 拼接）时也安全。
4. **BOLA 的本质是“有认证、无授权”**：不要只测越权查看，必须用 A/B 账号切换重放所有写操作（PUT、DELETE、PATCH）。
5. **老版本接口最容易漏补丁**：`/api/v2` 修了不代表 `/api/v1` 下线了，务必扫描版本化路径。
6. **业务逻辑漏洞往往回报最高**：它们无法被扫描器发现，且组合链往往能直接提权到管理员或造成资金损失。
7. **Race Condition 优先测试“一次性”操作，但不要忽略幂等操作**：优惠券、重置、试用是首选；修改密码、绑定邮箱也可能因竞态导致状态错乱。

---

## 4. 按需加载协议（执行规则）

当路由表命中某个攻击方向时，Agent 必须执行以下动作：

1. **加载**：使用 `read_file` 或其他工具，加载对应子技能路径下的完整 `SKILL.md` 内容到上下文。
2. **执行**：严格依照子技能中的测试步骤（快速命中 → 绕过技巧 → 深度利用）进行验证。
3. **逻辑卸载**：完成该方向测试后，不得在后续对话中重复粘贴或引用该子技能的冗长 payload 清单与绕过细节。应将测试结论压缩为 1-2 句摘要（如“SSRF 已测，仅出网无内网回显”），并在下一轮重路由时只依赖该摘要与本核心路由表。如需重新测试该方向，可再次加载原始文件，但不保留旧上下文。
4. **重路由**：基于本轮测试的响应（如新的报错信息、接口字段、响应头），重新对照路由表，决定下一轮加载哪个子技能。

---

## 5. 技能映射索引（参考）

> 此列表供快速查阅，不强制加载。实际加载请按路由表路径。

- Recon & Methodology: `../recon-and-methodology/SKILL.md`
- XSS: `../injection-checking/xss-cross-site-scripting/SKILL.md`
- SQLi: `../injection-checking/sqli-sql-injection/SKILL.md`
- SSRF: `../injection-checking/ssrf-server-side-request-forgery/SKILL.md`
- XXE: `../injection-checking/xxe-xml-external-entity/SKILL.md`
- SSTI: `../injection-checking/ssti-server-side-template-injection/SKILL.md`
- IDOR: `../auth-sec/idor-broken-object-authorization/SKILL.md`
- CMDi: `../injection-checking/cmdi-command-injection/SKILL.md`
- Path Traversal: `../path-traversal-lfi/SKILL.md`
- CSRF: `../auth-sec/csrf-cross-site-request-forgery/SKILL.md`
- API Security: `../api-sec/SKILL.md`
- JWT/OAuth: `../auth-sec/jwt-oauth-token-attacks/SKILL.md`
- OAuth/OIDC: `../auth-sec/oauth-oidc-misconfiguration/SKILL.md`
- CORS: `../auth-sec/cors-cross-origin-misconfiguration/SKILL.md`
- SAML: `../auth-sec/saml-sso-assertion-attacks/SKILL.md`
- Auth Bypass: `../auth-sec/authbypass-authentication-flaws/SKILL.md`
- Business Logic: `../business-logic-vuln/business-logic-vulnerabilities/SKILL.md`
- File Upload: `../upload-insecure-files/SKILL.md`
- Request Smuggling: `../injection-checking/request-smuggling/SKILL.md`
- Prototype Pollution: `../injection-checking/prototype-pollution/SKILL.md`
- HTTP Parameter Pollution: `../injection-checking/http-parameter-pollution/SKILL.md`
- Race Condition: `../race-condition/SKILL.md`
<!-- - XSLT Injection: `../injection-checking/xslt-injection/SKILL.md` -->
<!-- - CSV Formula Injection: `../injection-checking/csv-formula-injection/SKILL.md` -->
<!-- - Type Juggling: `../injection-checking/type-juggling/SKILL.md` -->

---

## 6. 启动提示词示例（Agent 自用）

当用户提供目标后，Agent 内部应如此启动：

> “目标已获取。我将先执行 Recon（检查 robots、sitemap、OpenAPI、JS 文件）。基于结果，我按 HackSkills 路由表匹配攻击面。若发现 IDOR 迹象，我将加载 IDOR 子技能；若发现 SSRF 迹象，加载 SSRF 子技能。每轮测试后我将重新评估，确保组合链不被遗漏。”

---

**替换完成后，你的 Agent 将自动遵守“长驻路由表 + 按需加载深度子技能”的规则，既大幅降低上下文占用，又不会丢失路由决策能力和组合链直觉。**