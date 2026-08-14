---
name: secondary-context-path-traversal
description: >-
  Backend/gateway route traversal playbook. Use when a public parameter (path segment, query param, or header) is
  concatenated into the path of an internal HTTP request — BFF, API gateway, reverse proxy, or microservice routing —
  so traversal happens against the backend's route space, not the filesystem.
---

# SKILL: Secondary Context Path Traversal（后端路径注入 / 网关路由穿越）

> **AI LOAD INSTRUCTION**: 与经典 LFI（读 `/etc/passwd`、PHP wrapper）不同，这里的漏洞点在**第二次请求**——公开参数被拼进「内部后端/网关请求的路径」，穿越发生在内部服务的**路由空间**而非文件系统。收益是打到内部-only 端点（`/actuator/env`、`/admin`、其他微服务），不是读文件。Base model 会把它误判成普通路径穿越，忽略掉「只换路径、不动 host」就能横向打内网这条链。

## 0. RELATED ROUTING

先确认你的入口属于哪一类，别混用：

- [Path Traversal / LFI](../.claude/skills/path-traversal-lfi/SKILL.md) —— 参数直接进文件系统（`include()`、`file_get_contents`、下载接口）。目标是**读文件**。
- [SSRF](../.claude/skills/injection-checking/ssrf-server-side-request-forgery/SKILL.md) —— 你能控制**完整 URL / host**。目标是**打任意内网地址与云元数据**。
- 本 skill —— 你只能控制**路径片段**（或路径 + 有限 header），host 由后端固定。目标是**打内部服务的路由表**。

### 三者判定（30 秒）

| 你控制的量 | 穿越空间 | 归入哪个 skill |
|---|---|---|
| 文件路径字符串 | 文件系统 | path-traversal-lfi |
| 完整 URL（含 scheme/host） | 网络地址 | ssrf |
| 仅路径/路由片段（host 固定） | 内部 API 路由 | **本 skill** |

---

## 1. CORE CONCEPT

```
用户 → 公开端点(前端/BFF/网关) → 后端拼接 → 内部服务
        ?path=xxx  ────────────────────────→  GET http://internal:8080/api/{xxx}
```

漏洞成立的两要素：
1. **拼接点**：`{xxx}` 直接进入内部请求的 URL 路径，未做规范化/白名单校验。
2. **二次上下文**：穿越作用于「内部服务的路由空间」，因此 payload 目标是内部路径（`/actuator/env`、`/admin/`、`/v1/internal/...`），**不是** `/etc/passwd`。

判据：如果注入 `/etc/passwd` 没有反应，但注入 `/actuator/env` 或 `../admin` 返回了不同形状的 JSON/错误，说明你面对的是**后端路由穿越**，不是文件 LFI。

---

## 2. RECOGNITION（无需源码的指纹特征）

满足 ≥2 条即值得深挖：

- [ ] 参数名是 `path`/`file`/`url`/`resource`/`target`/`route`/`forward`，但值像「资源 id」或「路径」，返回却是**结构化 JSON**（而非 HTML/文件字节流）。
- [ ] 响应头或错误里出现网关/上游痕迹：`X-Forwarded-*`、`Via:`、`Server: nginx/…`、Spring Cloud Gateway、`upstream connect error`、`no route to host`、`404 No Route`。
- [ ] 注入 `../` 或 `..;/` 时，状态码从 200 → 404/502/500，或错误体泄露内部路径/主机名（`java.io.FileNotFoundException` 只代表文件层，`Could not resolve`/`Connection refused to internal-host` 代表网络层）。
- [ ] 响应内容类型随参数跳变（`application/json` ↔ `text/html`），说明命中了不同的内部 handler。

> 注意：错误信息本身就是情报。`Connection refused to <internal-host>` 泄露了内网主机名，比拿到 200 更有价值——先记录，再测路由。

---

## 3. FIRST-PASS PAYLOADS（每端点 ≤5 次，见 §7）

先打这 5 个，看**响应差异**而非逐个爆破：

```text
../../../                       → 探测路由是否可上跳（观察状态码/内容类型变化）
/actuator/env                    → 绝对内部路径直连（BFF 常见：健康/配置端点）
..;/                            → 绕过只 strip ../ 的规范化（分号在部分解析器=路径分隔）
%2e%2e%2f                        → 一次编码穿越
../ + {已知内部路径片段}           → 结合 JS 里抓到的内部 API 前缀组合
```

**判定方式（响应差分）**：以未注入的基线响应为准，记录 4 个维度——`status`、`Content-Type`、`body 长度`、`是否出现内部错误关键词`。任一项相对基线突变 >30% 即标记为「路由命中」，进入 §4 定位。

---

## 4. SITUATIONAL PAYLOAD（按拼接方式选，不堆量）

根据后端拼接行为，二选一：

### A. 后端做「路径拼接 + 前缀固定」`prefix + user_input`

目标：上跳到路由根再横走。

| 场景 | payload |
|---|---|
| 简单拼接 | `../../` × n（n=1..3 足够，别再往上） |
| 过滤了 `../` | `....//`、`..././`、`..;/`、`..%2f`、`%2e%2e/` |
| 解码一次后过滤 | 双重编码 `%252e%252e%252f` |
| Java/Tomcat | `..;/`、`..%5c`（反斜杠） |
| 前缀已含目录 | 绝对路径 `/actuator/env` 直接试 |

### B. 后端做「URL 拼接 + 追加固定后缀」`base + user_input + suffix`

| 场景 | payload |
|---|---|
| 截断后缀 | `%00`（旧 PHP）、`?`、`#`（把后缀变成查询/锚点） |
| 保留查询 | `%3f`（把 `?` 当路径字符）、`%23`（`#` 当路径字符） |
| 需要二次编码 | `%252f`、`%253f` |

> 选型原则：**先判断 A/B 再打**，每类只打 2~3 个代表性 payload。别把 200 个组合一次扫完——那既违反限速，也会被 WAF 拉黑。

---

## 5. BFF / GATEWAY 专属技巧（本 skill 的差异化价值）

普通路径穿越不覆盖这些，但 BFF 场景下它们是主攻方向：

### 请求方法变换
内部 API 可能只收 POST，前端网关却放行 GET 拼接。测：同路径改用 `POST` + 合适 `Content-Type`，看是否命中原本 404/405 的内部端点。

### 路由改写类 Header（比路径遍历更稳）
不少网关/反向代理信任这些头来改写路由，值得在**路径注入同时**各试一次：

```text
X-Original-URL: /admin
X-Rewrite-URL:  /admin
X-Forwarded-Prefix: /admin
X-Forwarded-Host: internal-host
```

### Host 头切换
若内部网关按 `Host` 选 vhost/upstream，尝试把 `Host` 改成内部主机名（从前述报错里捞到的），可能直接命中内部管理站点。

### 时间差分确认盲点
当响应无差异但怀疑存在内部调用：比对「合法路径」与「注入路径」的 `response time`。内部服务被拖慢（如探测到超时、连接重试）可作为存在二次请求的旁证——但**只作辅助，不作唯一证据**。

---

## 6. VERIFICATION & FALSE-POSITIVE FILTER

命中「路由穿越」不等于有漏洞，逐条排除误报：

1. **确认是敏感内部端点**：返回内容须是内部能力/数据（actuator 配置、内部 admin、用户数据），而非公开也能拿到的内容。**公开文章、编辑信息、无敏感字段 → 忽略**（对齐 CLAUDE.md 原则）。
2. **区分「路由穿越」与「公开别名」**：用 Burp Repeater 重发一次，确认不是前端本来就暴露的别名路径。
3. **验证可深入**：打到 `/actuator/env` 后，继续取子键（如 `/actuator/env/spring.datasource.password`、`/actuator/health`、`/actuator/mappings`）证明能拿到**实际敏感值**，而非仅命中关键词。
4. **换 `Accept` 复测**：`application/json` ↔ `application/xml` 切换，确认不是前端对不同 Accept 的正常分流。

---

## 7. SAFETY & RATE LIMIT（硬约束，对齐 CLAUDE.md）

- **同端点请求总数 ≤ 5**（含重放与差分基线）。只打高价值参数，不做目录/参数爆破。
- **禁止**：DoS、`DROP`/`DELETE`、任何不可逆写操作 payload；禁止把穿越当跳板去碰数据库写操作。
- **预期先行**：每次发送前先写明「期望响应变化」（例：期望注入 `/actuator/env` 后 404 → 200 且返回 JSON 配置）。
- **Scope 锁定**：只测授权目标，忽略第三方资源；若用户直接给了 URL/原始请求，则该目标即范围。

---

## 8. ESCALATION（确认后的利用链）

```
路由穿越（打到内部路径）
├── /actuator/env → 读内部配置（DB 口令、密钥）→ 横向
├── /admin、/internal/* → 内部管理端点未授权访问 → 越权/接管
├── 报错泄露内部主机名 → 结合 SSRF/Host 头 → 打其它微服务
├── 方法变换命中 POST-only 端点 → 触发内部写操作（仅限只读验证）
└── 时间差分确认二次请求 → 定位上游，扩展攻击面
```

---

## 9. OUTPUT（严格格式）

确认风险后，按 CLAUDE.md 格式输出，**低危不报**：

```
[漏洞类型] 端点
- 原始: GET /api/resource/1?path=foo
- 变形: path=/actuator/env  （或 ../../../admin）
- 证据: 404→200，返回内部 JSON 配置（脱敏截图/字段）
- 建议: 后端拼接前做路径白名单/规范化，禁止用户输入进入内部请求路由
```

POC 与报告落到 `hack/`，中间文件落到 `temp/`。
