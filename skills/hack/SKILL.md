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

本技能采用 **长驻摘要 + 按需深度** 混合模式：

1. **长驻上下文（始终保留）**：以下「核心路由表」「7 条专家直觉」「判定阈值」必须始终保留在上下文窗口中，不得卸载。
2. **按需加载（仅在触发时加载）**：当路由表匹配到具体漏洞类别（如 XSS、SSRF、IDOR）时，立即从文件系统加载对应子技能的完整 `SKILL.md` 内容，执行测试；完成该方向测试后，卸载子技能内容，释放上下文窗口给其他模块。
3. **动态重路由**：在每轮子技能执行完毕后，Agent 必须基于新发现（如响应头、报错信息、新增接口）重新对照路由表，判断是否切换到其他攻击面。

---

## 1. 核心路由表（始终驻留）

**使用规则**：除「信息收集（Recon）」外，其余条目均按「现象」触发，命中即加载对应子技能。Recon 是**无条件第一步**，不依赖现象，须在任何其他测试前执行；其产出（端点清单、泄露线索）再作为现象触发后续条目。

> **现象来源（两类，均能触发路由）**：路由表「现象」列包含两类信号，**不是**仅靠 Recon 一次性给齐——
> 1. **攻击面现象（Recon 阶段可见，含信息泄露产出）**：端点结构、参数名（如 `?file=` `?id=` `?url=`）、技术栈、功能面（上传/登录/找回）、泄露的配置与密钥 → 决定「去哪里测」。
> 2. **响应现象（初探后才可见）**：对可疑参数发起无害初探后观察到的反射、报错、延时、响应头异常（`X-Cache`/`ACAO`）、状态码变化 → 决定「是什么漏洞」。
> 规则：Recon 给攻击面，初探响应的观察给漏洞信号；**二者任一命中路由表即加载对应子技能**，不得只测 Recon 显眼的参数而忽略初探响应里新冒出的现象。

> **直连 vs 二级分流**：路由表中「路径」若指向叶子技能（如 `xss-cross-site-scripting/SKILL.md`），**直接加载该叶子**，无需先读 P1 分类路由器；仅当需要在同族方向间做「二次观察」分流（例如不确定是 XSS 还是 SQLi，或需在 BOLA/BFLA/方法滥用之间抉择）时，才加载 P1 分类路由器（`api-sec` / `auth-sec` / `injection-checking` / `business-logic-vuln` / `file-access-vuln`）做二次分流。

> **路由权威唯一**：跨类路由（现象 → 顶层方向）唯一由本表决定。P1 方法论/路由器只做「本类内 P1→P2 下钻」，凡跨类方向一律把现象**回流本表**，不得直接指向兄弟 P1（如 recon-for-sec 不得直接路由到 api-sec）。

- **信息收集（Recon）**——无条件第一步（非现象触发），含「信息泄露」子方向
  - 路径：`../recon-for-sec/SKILL.md`（Recon 入口 + 完整方法论；静态发现与信息泄露线索的识别/转交均在其中）

- **XSS（跨站脚本）**
  - 现象：输入反射到 HTML / JS 属性 / DOM 操作
  - 路径：`../injection-checking/xss-cross-site-scripting/SKILL.md`

- **SSRF（服务端请求伪造）**
  - 现象：服务端主动访问 URL / 主机名（如头像、预览、Webhook）
  - 路径：`../injection-checking/ssrf-server-side-request-forgery/SKILL.md`

- **XXE（XML外部实体注入）**
  - 现象：接收 XML / Office / SVG / SOAP 请求
  - 路径：`../injection-checking/xxe-xml-external-entity/SKILL.md`

- **Path Traversal / LFI（路径遍历/本地文件包含）**
  - 现象：路径、文件名、下载接口参数可控（如 `?file=report.pdf`）
  - 路径：`../path-traversal-lfi/SKILL.md`

- **Secondary Context Path Traversal（二级上下文路径遍历）**
  - 现象：目标采用 BFF/网关模式，URL 参数值可能被拼接到后端微服务请求中；尝试注入 `../` 或绝对路径时出现 `No route to host`、`Connection refused`、upstream 404 等**网络层/路由层**错误；或公开端点返回 JSON/XML 内部数据。
  - 路径：`../path-traversal-lfi/secondary-context/SKILL.md`

- **IDOR / BOLA / BFLA（对象级/功能级授权绕过）**
  - 现象：API 路径或 JSON 中包含大量对象 ID（如 `/user/123`、`{"org_id": 456}`）
  - 路径：`../auth-sec/idor-broken-object-authorization/SKILL.md`

- **Auth Bypass / JWT / OAuth（认证绕过与令牌攻击）**
  - 现象：登录、注册、找回密码、2FA、Session 管理、JWT
  - 路径：`../auth-sec/authbypass-authentication-flaws/SKILL.md` 及 `../auth-sec/jwt-oauth-token-attacks/SKILL.md`

- **权限绕过（403 Bypass）**
  - 现象：路径返回 403（存在但被拒绝），或网关/WAF/反向代理层拒绝而怀疑后端未做同等校验
  - 路径：`../auth-sec/403-forbidden-bypass/SKILL.md`

- **Business Logic（业务逻辑漏洞）**
  - 现象：多步骤交易、优惠券、价格修改、库存扣减、状态机跳转（如 draft→paid→shipped）
  - 路径：`../business-logic-vuln/business-logic-vulnerabilities/SKILL.md`（同时交叉 Auth Bypass）

- **NoSQL Injection（NoSQL注入）**
  - 现象：MongoDB / JSON 查询语法参数（如 `?search[$ne]=1`）
  - 路径：`../injection-checking/nosql-injection/SKILL.md`

- **Command Injection（命令注入）**
  - 现象：命令执行类参数（如 `?ping=8.8.8.8`、`?convert=image.jpg`、导入器）
  - 路径：`../injection-checking/cmdi-command-injection/SKILL.md`

- **Request Smuggling（请求走私）**
  - 现象：HTTP 请求解析异常 / 前后端 CL.TE 或 TE.CL 分帧不一致 / HTTP/2 降级
  - 路径：`../injection-checking/request-smuggling/SKILL.md`

- **Prototype Pollution（原型链污染）**
  - 现象：Node.js 环境接收 JSON，且包含 `__proto__` 或 `constructor` 关键字
  - 路径：`../injection-checking/prototype-pollution/SKILL.md`

- **HTTP Parameter Pollution（HTTP参数污染）**
  - 现象：同名参数重复 / WAF 与后端应用解析顺序不一致
  - 路径：`../injection-checking/http-parameter-pollution/SKILL.md`

- **Race Condition（条件竞争）**
  - 现象：优惠券领取、密码重置、库存扣减、投票等一次性/限量操作
  - 路径：`../race-condition/SKILL.md`

- **Insecure File Upload（不安全文件上传）**
  - 现象：文件上传功能
  - 路径：`../upload-insecure-files/SKILL.md`

- **GraphQL API Security**
  - 现象：GraphQL 端点（`/graphql`、`/v1/graphql`）
  - 路径：`../api-sec/graphql-and-hidden-parameters/SKILL.md`

- **Web Cache Poisoning（Web缓存投毒）**
  - 现象：响应头含 `X-Cache`/`X-Varnish`/`CF-Cache-Status`，且 `X-Forwarded-Host`/`X-Original-URL`/`Host` 可控，可投毒缓存命中其他用户
  - 路径：`../web-cache-poisoning/SKILL.md`

- **Web Cache Deception（Web缓存欺骗）**
  - 现象：缓存把带路径混淆的敏感认证内容（如 `/account/..%2fprofile.css`）错误缓存并泄露给其他用户
  - 路径：`../web-cache-deception/SKILL.md`

- **SQL Injection（SQL注入）**
  - 现象：参数值含 `'` `"` `\` 返回 SQL 错误或响应延时变化
  - 路径：`../injection-checking/sqli-sql-injection/SKILL.md`

- **SSTI（服务端模板注入）**
  - 现象：参数值含 `{{` `}}` `${}` `#{` 且响应回显计算值或报模板错误
  - 路径：`../injection-checking/ssti-server-side-template-injection/SKILL.md`

- **Mass Assignment（批量赋值）**
  - 现象：JSON 请求体中包含非文档字段（如 `role`、`is_admin`、`permission`、`group`）且被接受
  - 路径：`../api-sec/api-authorization-and-bola/SKILL.md`（其 §2/§3 覆盖隐藏可写字段与 Mass Assignment）

- **CORS Misconfiguration（跨域资源共享配置错误）**
  - 现象：响应头包含 `Access-Control-Allow-Origin: *` 或 `null`，且带 `Access-Control-Allow-Credentials: true`
  - 路径：`../auth-sec/cors-cross-origin-misconfiguration/SKILL.md`

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

## 3.5 判定阈值（常驻，不可卸载）

> 这些阈值决定「是否值得测 / 是否值得报」。加载任何叶子技能执行时都必须套用，防止误报低危。

1. **未授权访问**：须泄露敏感数据（姓名、身份证、银行卡、手机号、密码、家庭地址 等 **≥3 个字段** 的组合），否则忽略。
2. **CORS**：接口必须能泄露用户敏感数据（如 PII），否则视为无效，不深入。
3. **OSS STS**：临时 STS 凭证仅用于特定文件上传，忽略。
4. **低危漏洞**：忽略，不深入、不写入报告。
5. **Clickjacking**：忽略。

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

- Recon 入口 + 方法论: `../recon-for-sec/SKILL.md`
- Insecure Source Code Management: `../insecure-source-code-management/SKILL.md`
- Dependency Confusion: `../dependency-confusion/SKILL.md`
- XSS: `../injection-checking/xss-cross-site-scripting/SKILL.md`
- SQLi: `../injection-checking/sqli-sql-injection/SKILL.md`
- NoSQL Injection: `../injection-checking/nosql-injection/SKILL.md`
- SSRF: `../injection-checking/ssrf-server-side-request-forgery/SKILL.md`
- XXE: `../injection-checking/xxe-xml-external-entity/SKILL.md`
- SSTI: `../injection-checking/ssti-server-side-template-injection/SKILL.md`
- IDOR: `../auth-sec/idor-broken-object-authorization/SKILL.md`
- CMDi: `../injection-checking/cmdi-command-injection/SKILL.md`
- Path Traversal: `../path-traversal-lfi/SKILL.md`
- Secondary Context Path Traversal: `../path-traversal-lfi/secondary-context/SKILL.md`
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
- Web Cache Poisoning: `../web-cache-poisoning/SKILL.md`
- Web Cache Deception: `../web-cache-deception/SKILL.md`
<!-- - XSLT Injection: `../injection-checking/xslt-injection/SKILL.md` -->
<!-- - CSV Formula Injection: `../injection-checking/csv-formula-injection/SKILL.md` -->
<!-- - Type Juggling: `../injection-checking/type-juggling/SKILL.md` -->

---

## 6. 启动提示词示例（Agent 自用）

当用户提供目标后，Agent 内部应如此启动：

> “目标已获取。我将先执行 Recon（检查 robots、sitemap、OpenAPI、JS 文件）。基于结果，我按 HackSkills 路由表匹配攻击面。若发现 IDOR 迹象，我将加载 IDOR 子技能；若发现 SSRF 迹象，加载 SSRF 子技能。每轮测试后我将重新评估，确保组合链不被遗漏。”

---

**替换完成后，你的 Agent 将自动遵守“长驻路由表 + 按需加载深度子技能”的规则，既大幅降低上下文占用，又不会丢失路由决策能力和组合链直觉。**