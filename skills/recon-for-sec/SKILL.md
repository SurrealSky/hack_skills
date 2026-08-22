---
name: recon-for-sec
description: >-
  Entry P1 category router for reconnaissance and methodology. Use when mapping
  scope, discovering assets, fingerprinting technology, building endpoint
  inventory, and choosing the first high-value security testing path.
---

# SKILL: Recon and Methodology — Expert Bug Bounty Playbook

> **AI LOAD INSTRUCTION**: Systematic recon and bug-finding methodology from top bug hunters. Covers subdomain enumeration, endpoint discovery, tech fingerprinting, and the hunter's mental model for finding bugs that others miss. Key insight: most high-severity bugs are found through systematic coverage, not just clever payloads.

---

## 授权分级路由（RoE Gate，必须第一步执行）

接新目标前，先按目标授权范围判定 RoE 级别（见 CLAUDE.md「目标授权分级」），再决定走哪条流程：

| RoE 级别 | 可执行的章节 |
|---|---|
| `ROE-PASSIVE`（默认） | §2 Passive、§4、§5 JavaScript Source Mining、§6 GitHub dork；其余标注 `[需 ROE-AGGRESSIVE]` / `[ROE-HYBRID]` 的跳过 |
| `ROE-HYBRID` | PASSIVE 全部 + §10/§12/§13 等已知路径点测（≤N 个高价值路径，非 wordlist 爆破） |
| `ROE-AGGRESSIVE` | 全部章节可用 |

> 判定规则：默认 `ROE-PASSIVE`；只有目标/用户明确授权才升级。任何标注了级别的章节，超出当前级别的直接跳过，不得越级。

---

## 0. 入口与下钻路由（Entry & Sub-skill Routing）

这是新目标和未知攻击面的起始入口。

> **路由权威唯一化（避免与 hack 冲突）**：跨类路由的唯一权威是 **hack 核心路由表**。本技能（P1 方法论）只做「本类内下钻」（→ `insecure-source-code-management` / `dependency-confusion`）；凡命中跨类方向（api-sec / auth-sec / injection-checking / business-logic-vuln / file-access-vuln），一律把「现象」**回流 hack**，由 hack 统一决策，本技能不直接指向兄弟 P1。

### When to Use

- 你刚接一个新的目标，还不知道先测什么
- 你需要先做资产发现、技术识别、接口清点和测试路线规划
- 你想把后续测试建立在结构化方法论上，而不是随机枚举 payload

### 下钻专项（Sub-skills）

- [Insecure Source Code Management](../insecure-source-code-management/SKILL.md) — VCS/备份泄露（.git/.svn/.hg/.bzr/.DS_Store/.env）检测与恢复
- [Dependency Confusion](../dependency-confusion/SKILL.md) — 供应链侦察：内部包名泄露 → 公开注册表抢占（仅授权环境做 PoC）

### Recommended Flow

1. 先确认 in-scope 资产和目标类型
2. 再做资产发现、端口与服务识别、技术指纹与端点收集
3. 收集到的「现象」回流 hack 核心路由表，由 hack 决策加载哪个方向（api-sec / auth-sec / injection-checking / business-logic-vuln 等）

---

## 1. RECON HIERARCHY

```
Target Selection
└── Scope Definition (in-scope assets)
    └── Asset Discovery (subdomains, IPs, domains)
        └── Tech Fingerprinting (what's running)
            └── Endpoint Discovery (attack surface)
                └── Vulnerability Testing (per vulnerability type)
```

---

## 2. SUBDOMAIN ENUMERATION (CRITICAL FIRST STEP)

### Passive (no DNS queries to target) [ROE-PASSIVE 可用]
```bash
# Subfinder (aggregates multiple sources):
subfinder -d target.com -o subdomains.txt

# Amass passive:
amass enum -passive -d target.com

# Certsh (certificate transparency):
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq -r '.[].name_value' | sort -u

# SecurityTrails API, Shodan:
# Web: https://securitytrails.com/list/apex_domain/target.com
```

### Active (DNS brute force + resolution) [需 ROE-AGGRESSIVE]
```bash
# Massdns + wordlist:
massdns -r /path/to/resolvers.txt -t A -o S -w output.txt \
  <(cat wordlist.txt | sed 's/$/.target.com/')

# ffuf for subdomain brute:
ffuf -w subdomains-wordlist.txt -u https://FUZZ.target.com \
  -mc 200,301,302,403 -H "Host: FUZZ.target.com"

# DNSx for bulk resolution:
cat subdomains.txt | dnsx -a -resp -o resolved.txt

# Recommended wordlist: SecLists/Discovery/DNS/
```

### Virtual Host Discovery [需 ROE-AGGRESSIVE]
```bash
# ffuf vhost mode:
ffuf -w wordlist.txt -u https://target.com \
  -H "Host: FUZZ.target.com" -mc 200,301,403

# gobuster vhost:
gobuster vhost -u https://target.com -w wordlist.txt
```

---

## 3. SERVICE AND PORT DISCOVERY [需 ROE-AGGRESSIVE]

```bash
# Fast port scan (common ports):
nmap -T4 -F target.com -oN ports.txt

# Comprehensive scan on resolved subdomains:
cat resolved_ips.txt | nmap -iL - --open -p 80,443,8080,8443,8888,3000,5000 -oG scan.txt

# httpx for HTTP probing:
cat subdomains.txt | httpx -title -tech-detect -status-code -o live_hosts.txt

# masscan for speed on large IP ranges:
masscan -p 80,443,8080,8443 10.0.0.0/8 --rate=1000
```

---

## 4. WEB TECHNOLOGY FINGERPRINTING [ROE-PASSIVE 可用（仅对已知/已访问资产）]

```bash
# Wappalyzer (browser extension) or:
whatweb https://target.com

# httpx with tech detection:
httpx -u https://target.com -tech-detect

# Check headers manually:
curl -sI https://target.com | grep -i "server\|x-powered-by\|x-generator\|cf-ray"

# Fingerprint from:
- Server header: nginx/1.18, Apache/2.4, IIS/10.0
- X-Powered-By: PHP/7.4, ASP.NET
- Cookies: PHPSESSID (PHP), JSESSIONID (Java), _rails_session (Rails)
- HTML comments: <!-- Drupal 9 -->
- Meta generator: <meta name="generator" content="WordPress 6.2">
- JS framework files: /static/js/angular.min.js
```

---

## 5. ENDPOINT DISCOVERY

### Static Discovery Files [ROE-PASSIVE 可用]
```bash
# 静态发现文件（先于任何暴力枚举，直接取现成路径清单）:
test: /robots.txt /sitemap.xml /security.txt /humans.txt /crossdomain.xml

# robots.txt       → Disallow 路径（隐藏目录/后台线索）
# sitemap.xml      → 全量 URL 清单（真实路径，直接作为端点候选）
# security.txt     → 安全联系人/披露策略
# humans.txt       → 团队/技术栈线索
# crossdomain.xml  → Flash 跨域策略（可能暴露可信域）
# .well-known/     → openid-configuration / security.txt / assetlinks.json 等
```
> 产物（真实路径、隐藏目录）作为「现象」回流 hack 路由表，命中其余条目即加载对应技能。

### Directory Brute Force [需 ROE-AGGRESSIVE]
```bash
# ffuf (fastest):
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt \
  -mc 200,301,302,403 -t 50 -o dirs.txt

# Gobuster:
gobuster dir -u https://target.com -w wordlist.txt -x php,html,js,json

# feroxbuster (recursive):
feroxbuster -u https://target.com -w wordlist.txt -x php,html,txt -r
```

### Parameter Discovery [需 ROE-AGGRESSIVE]
```bash
# Arjun (hidden parameter finder):
arjun -u https://target.com/api/endpoint

# x8:
x8 -u https://target.com/api/endpoint -w params-wordlist.txt
```

### JavaScript Source Mining [ROE-PASSIVE 可用]
```bash
# Extract endpoints from JS files:
gau target.com | grep '\.js$' | httpx -mc 200 | xargs -I{} curl -s {} | \
  grep -oE '"/[a-zA-Z0-9/_-]+"' | sort -u

# 顺带 grep JS 中泄露的密钥/内部路径（信息泄露线索）:
gau target.com | grep '\.js$' | httpx -mc 200 | xargs -I{} curl -s {} | \
  grep -oiE '(api[_-]?key|secret|token|password|sk_live_[a-z0-9]+)' | sort -u

# LinkFinder:
python3 linkfinder.py -i https://target.com -d -o output.html

# GetAllURLs (gau):
gau target.com | sort -u > all_urls.txt

# Wayback URLs:
waybackurls target.com | sort -u > wayback_urls.txt
```

### API Endpoint Discovery [需 ROE-AGGRESSIVE（Swagger/GraphQL 已知路径点测可用 ROE-HYBRID）]
```bash
# Common API paths:
ffuf -u https://target.com/FUZZ -w /SecLists/Discovery/Web-Content/api/api-endpoints.txt

# Swagger/OpenAPI:
test: /swagger.json /api-docs /openapi.json /v2/api-docs /.well-known/ /docs/

# GraphQL:
test: /graphql /gql /v1/graphql /api/graphql
```

---

## 6. SOURCE CODE RECON [ROE-PASSIVE 可用（GitHub dork）/ ROE-HYBRID（敏感文件点测）]

### GitHub / GitLab Exposure
```bash
# trufflehog (secret scanner in git history):
trufflehog git https://github.com/target-org/target-repo

# gitleaks:
gitleaks detect --source /path/to/cloned/repo

# Manual GitHub search:
# site:github.com "target.com" "api_key" OR "secret" OR "password"
# site:github.com "target.com" ".env" OR "config.php" OR "db_password"

# GitHub dorks:
# "target.com" extension:env
# "target.com" filename:*.config password
# org:target-org secret OR password OR apikey
```

### Exposed Environment Files
```
# Check common paths:
https://target.com/.env
https://target.com/.git/config
https://target.com/config.json
https://target.com/config.yaml
https://target.com/credentials.json
https://target.com/secrets.json
https://target.com/wp-config.php
https://target.com/backup.sql
https://target.com/backup.zip
```

---

## 7. ZSEANO'S TESTING METHODOLOGY

### Core Philosophy
1. **Go deep on one program** rather than spread across many — learn the application thoroughly
2. **Build a profile of the company** — tech stack, developers, processes
3. **Look where others don't** — check error pages, admin paths, old versions, mobile API
4. **Follow the filter** — if input is filtered somewhere, that functionality exists and may be bypassed

### Testing Sequence (One Page / Feature)
```
For each input point:
1. Non-malicious HTML tags (<h2>, <img>) → are they reflected?
2. Incomplete tags → what happens? (<iframe src=//evil.com )
3. Encoding tests → %0d, %0a, %09, <%00
4. Observe the OUTPUT too (not just response) — where does your input appear?
5. Test same input in ALL similarly-structured pages (shared code → shared vuln)
6. Check if the same parameter exists in mobile/API endpoint (less protected)
```

### Parameter Insights
```
- Each parameter tells a story: "what does this do server-side?"
- Filename → OS interaction → Path Traversal / CMDi
- URL/location → HTTP fetch → SSRF
- Template/HTML parameter → render function → SSTI
- XML field → parser → XXE
- SQL filter → query → SQLi
- User-content → storage → Stored XSS
```

---

## 8. BUG BOUNTY PROGRAM TRIAGE (WHERE TO SPEND TIME)

### High-Value Target Selection
```
✓ Programs with large scope (*.target.com)
✓ Programs that pay for P2/P3 (not just RCE)
✓ Programs with recent tech changes (migrations = new bugs)
✓ Programs with active development (new features = new attack surface)
× Avoid: frozen/old codebases with well-known CVEs (already claimed)
× Avoid: strict programs with narrow scope (less surface)
```

### High-Value Feature Focus (by bug probability)
```
Priority 1: Authentication, password reset, 2FA → account takeover
Priority 2: File upload, profile edit, API endpoints → stored XSS, IDOR
Priority 3: Admin panels, user management → BFLA, privilege escalation
Priority 4: Payment flows, subscription → business logic
Priority 5: Import/export, template rendering → XXE, SSTI
```

---

## 9. NUCLEI TEMPLATES (AUTOMATED SCANNING) [需 ROE-AGGRESSIVE]

```bash
# Run all on target:
nuclei -u https://target.com -t /nuclei-templates/ -o nuclei-results.txt

# Specific categories:
nuclei -u https://target.com -t cves/ -severity critical,high
nuclei -u https://target.com -t exposures/
nuclei -u https://target.com -t misconfiguration/

# On subdomain list:
cat subdomains.txt | nuclei -t exposures/ -t misconfiguration/ -o exposed.txt
```

---

## 10. COMMON MISCONFIGURATIONS (QUICK WINS) [ROE-HYBRID（已知路径点测）]

```
□ CORS: Access-Control-Allow-Origin: * with credentials → CSRF + data theft
□ S3 bucket public: curl https://target.s3.amazonaws.com/
□ Directory listing: response contains "Index of /"
□ .git exposed: curl https://target.com/.git/config
□ .env exposed: curl https://target.com/.env
□ Debug mode: stack traces in production (source code exposure)
□ Default credentials: admin:admin, admin:password on admin panels
□ phpinfo.php: curl https://target.com/phpinfo.php
□ Backup files: config.bak, database.sql.gz, app.zip
□ GraphQL introspection enabled: POST /graphql {"query":"{__schema{types{name}}}"}
□ Admin panels: /admin /manager /console /phpmyadmin /wp-admin
```

---

## 11. QUICK REFERENCE TOOLS

| Category | Tool |
|---|---|
| Subdomain enum | subfinder, amass, massdns |
| Port scan | nmap, masscan |
| HTTP probe | httpx |
| Dir brute | ffuf, feroxbuster, gobuster |
| JS mining | LinkFinder, gau, waybackurls |
| Secret scan | trufflehog, gitleaks |
| Parameter fuzz | arjun, x8 |
| Vuln scan | nuclei |
| Proxy/intercept | Burp Suite Pro |
| JWT attacks | jwt_tool |
| SQLi | sqlmap |
| XSS | dalfox, XSStrike |
| SSRF | SSRFmap, Gopherus |

---

## 12. JAVA MIDDLEWARE FINGERPRINT MATRIX [ROE-HYBRID（已知路径点测）]

| Middleware | Detection Path | Key Indicators |
|---|---|---|
| Apache Tomcat | `/manager/html`, `/manager/status` | Default creds: `tomcat:tomcat`, `admin:admin` |
| JBoss / WildFly | `/jmx-console/`, `/web-console/` | JMX MBean access, WAR deployment |
| WebLogic | `/console/`, `/wls-wsat/` | T3 protocol on 7001/7002, IIOP |
| Spring Boot Actuator | `/actuator/`, `/actuator/env`, `/actuator/heapdump` | JSON endpoint listing, heap dump contains secrets |
| Spring Boot (alt paths) | `/actuator/jolokia`, `/actuator/gateway/routes` | Jolokia JMX bridge, Gateway route injection |
| Jenkins | `/script`, `/manage` | Groovy console, API token in cookie |
| GlassFish | `/common/`, `/theme/` | Admin on 4848, default empty password |
| Jetty | `/jolokia/` | JMX access |
| Resin | `/resin-admin/` | Admin panel |

### Spring Boot Actuator Exploitation Priority

```
/actuator/env          → Leak environment variables (DB creds, API keys)
/actuator/heapdump     → Download JVM heap → search for passwords in memory
/actuator/jolokia      → JMX → possible RCE via MBean manipulation
/actuator/gateway/routes → Spring Cloud Gateway → SpEL injection (CVE-2022-22947)
/actuator/configprops  → All configuration properties
/actuator/mappings     → All URL mappings (hidden endpoints)
/actuator/beans        → All Spring beans
/actuator/shutdown     → POST to shutdown application (DoS)
```

---

## 13. INFORMATION LEAK（信息泄露线索）→ 识别后转交深挖 [ROE-HYBRID（已知路径点测）]

> 本节只做**线索识别 + 转交**，不再重复罗列 VCS/备份/密钥的探测路径（已收敛至 `insecure-source-code-management`，作为「信息泄露」漏洞类型的**唯一深度技能**，避免与上文章节重复）。
> 定位：hack 核心路由表中「信息泄露」已并入 Recon（不再单列），本节即该子方向在 recon 内的落点。

- 命中 `.git/` `.svn/` `.hg/` `.bzr/` `.DS_Store`、`/backup.zip` `/dump.sql` `/.env` 等 VCS/备份/配置泄露 → 加载 [insecure-source-code-management](../insecure-source-code-management/SKILL.md) 深挖（**本类内下钻**，唯一直接落点）。
- 命中 `/.aws/credentials` `/.docker/config.json` 等运行时密钥 → 同上提取；命中凭证后**回流 hack**（凭证现象 → 由 hack 路由 Auth Bypass / API Security）。
- 命中 `/swagger-ui/` `/v3/api-docs` `/graphql` `/graphiql` `/phpinfo.php` `/server-status` 等 **API 文档/调试端点** → 属于**攻击面发现（端点发现），不是信息泄露**，**回流 hack**（由 hack 路由到 api-sec 等方向）。
- 命中 `/robots.txt` `/sitemap.xml` `/crossdomain.xml` `/.well-known/` → 属于 Recon 基础发现（见 §5 静态发现文件），非信息泄露。
