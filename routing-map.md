# HackSkills 路由图（P0 → P1 → P2）

> 本文件是 `.claude/skills/` 技能体系的**全量路由索引**，供快速查阅与决策依据。
> 运行时以 `.claude/skills/hack/SKILL.md` 的核心路由表为准；本文件只做结构汇总，不替代路由表。
> 更新本文件时，同步检查 hack/SKILL.md 的路由表是否一致。

---

## 一、路由原理

```
约束层  CLAUDE.md（RoE / RateLimit≤5 / Safe Payload / 报告格式）── 横向贯穿每一步
路由层  Skill 体系（现象 → P0 → P1 → P2）── 纵向逐级下钻
```

- **P0 `hack`**：核心路由表，按「现象」命中攻击方向，常驻上下文。
- **P1 分类路由器**：带子技能的按更细「观察」二次下钻；单叶子的由 hack 直接落点。
- **P2 叶子技能**：具体 playbook，**按需加载**（`read_file`），测完**逻辑卸载**压缩成摘要。
- **动态重路由**：每轮测试后基于新发现（响应头/报错/新接口）重新对照路由表。
- **RoE Gate**：路由前必须先判授权级别，超出当前级别的章节一律跳过。

---

## 二、全量路由树

```
P0  hack/SKILL.md ── 核心路由表（现象 → 方向，长驻）
│
├─ 现象：robots/sitemap/swagger/graphql/js 可访问
│   └─ P1 recon-for-sec ── 授权分级 RoE Gate（第一步硬门）
│        ├─ P2 insecure-source-code-management  .git/.svn/.hg/.bzr/.env/备份.zip
│        ├─ P2 dependency-confusion            内部包名 → 公开注册表抢占
│        └─ 出口 → api-sec / auth-sec / injection-checking / business-logic-vuln
│
├─ 现象：REST API / 移动端后端 / OpenAPI 文档
│   └─ P1 api-sec ─────────────────────────────
│        ├─ P2 api-recon-and-docs              Swagger/版本漂移/隐藏文档
│        ├─ P2 api-authorization-and-bola      BOLA/BFLA/方法滥用/隐藏可写字段
│        ├─ P2 api-auth-and-jwt-abuse          Bearer/Header 信任/Claim/限流绕过
│        └─ P2 graphql-and-hidden-parameters   introspection/batching/隐藏参数
│
├─ 现象：登录/注册/找回密码/2FA/Session/JWT/OAuth/SSO
│   └─ P1 auth-sec ────────────────────────────
│        ├─ P2 authbypass-authentication-flaws   登录绕过/2FA/枚举/爆破防护
│        ├─ P2 idor-broken-object-authorization  IDOR/BOLA/BFLA/对象授权
│        ├─ P2 jwt-oauth-token-attacks           算法混淆/密钥信任/Claim/Token伪造
│        ├─ P2 oauth-oidc-misconfiguration       redirect_uri/state/nonce/PKCE/账号绑定
│        ├─ P2 csrf-cross-site-request-forgery   CSRF token/SameSite/JSON CSRF
│        ├─ P2 cors-cross-origin-misconfiguration 反射Origin/凭证化跨域/白名单绕过
│        └─ P2 saml-sso-assertion-attacks        assertion wrapping/签名/Audience
│
├─ 现象：输入进入 HTML/SQL/模板/URL提取器/XML/shell
│   └─ P1 injection-checking ───────────────────
│        ├─ P2 xss-cross-site-scripting
│        ├─ P2 sqli-sql-injection
│        ├─ P2 ssrf-server-side-request-forgery
│        ├─ P2 xxe-xml-external-entity
│        ├─ P2 ssti-server-side-template-injection
│        ├─ P2 cmdi-command-injection
│        ├─ P2 nosql-injection
│        ├─ P2 deserialization-insecure
│        ├─ P2 jndi-injection
│        ├─ P2 expression-language-injection
│        ├─ P2 crlf-injection
│        ├─ P2 request-smuggling
│        ├─ P2 prototype-pollution
│        ├─ P2 http-parameter-pollution
│        ├─ P2 xslt-injection            (hack 路由表已注释)
│        ├─ P2 csv-formula-injection     (hack 路由表已注释)
│        ├─ P2 type-juggling             (hack 路由表已注释)
│        └─ P2 EXTRA_INJECTION_TYPES.md  (SSI / LDAP / XPath)
│
├─ 现象：优惠券/库存/支付/审批/配额/邀请/状态流转
│   └─ P1 business-logic-vuln ──────────────────
│        └─ P2 business-logic-vulnerabilities
│
├─ 现象：文件路径/下载/上传/预览/解压/分享
│   └─ P1 file-access-vuln ─────────────────────
│        ├─ P2 path-traversal-lfi
│        └─ P2 upload-insecure-files
│
└─ 单叶方向（hack 直接路由到叶子，无中间 P1 路由器）
     ├─ P2 path-traversal-lfi ──┐
     │    └─ P2 secondary-context   BFF/网关二级上下文路径遍历
     ├─ P2 insecure-source-code-management  VCS/备份/.env 泄露
     ├─ P2 open-redirect                    开放重定向
     ├─ P2 race-condition                   条件竞争（交叉 business-logic）
     ├─ P2 upload-insecure-files            文件上传 → 可链 XSS/XXE/CMDi/traversal
     ├─ P2 web-cache-deception              缓存欺骗（窃取认证内容）
     ├─ P2 web-cache-poisoning              缓存投毒（X-Forwarded-Host/Host）
     └─ P2 dependency-confusion             供应链依赖混淆
```

---

## 三、目录索引（按磁盘路径）

### P0
| 技能 | 路径 | 角色 |
|---|---|---|
| hack | `.claude/skills/hack/SKILL.md` | 主路由（现象→方向） |

### P1 分类路由器（6 个，含子技能）
| 技能 | 路径 | 子技能数 |
|---|---|---|
| recon-for-sec | `.claude/skills/recon-for-sec/SKILL.md` | 2 + 出口 |
| api-sec | `.claude/skills/api-sec/SKILL.md` | 4 |
| auth-sec | `.claude/skills/auth-sec/SKILL.md` | 7 |
| injection-checking | `.claude/skills/injection-checking/SKILL.md` | 18（含 EXTRA + 3 注释） |
| business-logic-vuln | `.claude/skills/business-logic-vuln/SKILL.md` | 1 |
| file-access-vuln | `.claude/skills/file-access-vuln/SKILL.md` | 2（交叉引用） |

### P1 单叶（8 个，hack 直接落点）
| 技能 | 路径 |
|---|---|
| insecure-source-code-management | `.claude/skills/insecure-source-code-management/SKILL.md` |
| dependency-confusion | `.claude/skills/dependency-confusion/SKILL.md` |
| open-redirect | `.claude/skills/open-redirect/SKILL.md` |
| path-traversal-lfi | `.claude/skills/path-traversal-lfi/SKILL.md` |
| race-condition | `.claude/skills/race-condition/SKILL.md` |
| upload-insecure-files | `.claude/skills/upload-insecure-files/SKILL.md` |
| web-cache-deception | `.claude/skills/web-cache-deception/SKILL.md` |
| web-cache-poisoning | `.claude/skills/web-cache-poisoning/SKILL.md` |

### P2 叶子技能全表（35 个）
| 所属 P1 | 叶子技能 | 路径 |
|---|---|---|
| recon-for-sec | insecure-source-code-management | `insecure-source-code-management/SKILL.md` |
| recon-for-sec | dependency-confusion | `dependency-confusion/SKILL.md` |
| api-sec | api-recon-and-docs | `api-sec/api-recon-and-docs/SKILL.md` |
| api-sec | api-authorization-and-bola | `api-sec/api-authorization-and-bola/SKILL.md` |
| api-sec | api-auth-and-jwt-abuse | `api-sec/api-auth-and-jwt-abuse/SKILL.md` |
| api-sec | graphql-and-hidden-parameters | `api-sec/graphql-and-hidden-parameters/SKILL.md` |
| auth-sec | authbypass-authentication-flaws | `auth-sec/authbypass-authentication-flaws/SKILL.md` |
| auth-sec | idor-broken-object-authorization | `auth-sec/idor-broken-object-authorization/SKILL.md` |
| auth-sec | jwt-oauth-token-attacks | `auth-sec/jwt-oauth-token-attacks/SKILL.md` |
| auth-sec | oauth-oidc-misconfiguration | `auth-sec/oauth-oidc-misconfiguration/SKILL.md` |
| auth-sec | csrf-cross-site-request-forgery | `auth-sec/csrf-cross-site-request-forgery/SKILL.md` |
| auth-sec | cors-cross-origin-misconfiguration | `auth-sec/cors-cross-origin-misconfiguration/SKILL.md` |
| auth-sec | saml-sso-assertion-attacks | `auth-sec/saml-sso-assertion-attacks/SKILL.md` |
| business-logic-vuln | business-logic-vulnerabilities | `business-logic-vuln/business-logic-vulnerabilities/SKILL.md` |
| injection-checking | xss-cross-site-scripting | `injection-checking/xss-cross-site-scripting/SKILL.md` |
| injection-checking | sqli-sql-injection | `injection-checking/sqli-sql-injection/SKILL.md` |
| injection-checking | ssrf-server-side-request-forgery | `injection-checking/ssrf-server-side-request-forgery/SKILL.md` |
| injection-checking | xxe-xml-external-entity | `injection-checking/xxe-xml-external-entity/SKILL.md` |
| injection-checking | ssti-server-side-template-injection | `injection-checking/ssti-server-side-template-injection/SKILL.md` |
| injection-checking | cmdi-command-injection | `injection-checking/cmdi-command-injection/SKILL.md` |
| injection-checking | nosql-injection | `injection-checking/nosql-injection/SKILL.md` |
| injection-checking | deserialization-insecure | `injection-checking/deserialization-insecure/SKILL.md` |
| injection-checking | jndi-injection | `injection-checking/jndi-injection/SKILL.md` |
| injection-checking | expression-language-injection | `injection-checking/expression-language-injection/SKILL.md` |
| injection-checking | crlf-injection | `injection-checking/crlf-injection/SKILL.md` |
| injection-checking | request-smuggling | `injection-checking/request-smuggling/SKILL.md` |
| injection-checking | prototype-pollution | `injection-checking/prototype-pollution/SKILL.md` |
| injection-checking | http-parameter-pollution | `injection-checking/http-parameter-pollution/SKILL.md` |
| injection-checking | xslt-injection | `injection-checking/xslt-injection/SKILL.md` * |
| injection-checking | csv-formula-injection | `injection-checking/csv-formula-injection/SKILL.md` * |
| injection-checking | type-juggling | `injection-checking/type-juggling/SKILL.md` * |
| injection-checking | EXTRA_INJECTION_TYPES (SSI/LDAP/XPath) | `injection-checking/EXTRA_INJECTION_TYPES.md` |
| file-access-vuln | path-traversal-lfi | `path-traversal-lfi/SKILL.md` |
| file-access-vuln | upload-insecure-files | `upload-insecure-files/SKILL.md` |
| path-traversal-lfi | secondary-context | `path-traversal-lfi/secondary-context/SKILL.md` |

> `*` = 在 hack 核心路由表中已注释（未激活），但磁盘文件存在，可在 `ROE-AGGRESSIVE` 或明确需要时手动加载。

---

## 四、交叉引用与回环（非严格树形）

多个叶子技能互相指向，形成**有回环的图**，这是「动态重路由」与「组合链」机制存在的原因：

| 源技能 | 交叉指向 |
|---|---|
| upload-insecure-files | xss / xxe / cmdi / path-traversal / business-logic |
| race-condition | business-logic-vulnerabilities（双向） |
| recon-for-sec | api-sec / auth-sec / injection-checking / business-logic-vuln |
| path-traversal-lfi | upload-insecure-files |
| file-access-vuln | injection-checking / business-logic-vuln |
| insecure-source-code-management | recon-for-sec |
| dependency-confusion | recon-for-sec |

---

## 五、hack 路由表中已注释（未激活）的方向

```text
XSLT Injection      → injection-checking/xslt-injection/SKILL.md
CSV Formula Injection → injection-checking/csv-formula-injection/SKILL.md
Type Juggling       → injection-checking/type-juggling/SKILL.md
```

激活方式：在 hack/SKILL.md 取消对应 `<!-- ... -->` 注释，并同步更新本文件第三节的 `*` 标记。

---

## 六、维护约定

1. 新增/删除叶子技能时，同步更新：hack/SKILL.md 路由表 + 本文件。
2. 注释/激活某个方向时，同步 `*` 标记。
3. 路径统一使用 `.claude/skills/` 相对根，避免绝对路径失效。
