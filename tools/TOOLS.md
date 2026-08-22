# 本地工具注册表（Tools Registry）

> 本文件是 `./tools` 目录的**工具列表**，是判断「某个 CLI 能不能调用」的唯一依据。看最后一列「状态」：
>
> - ✅ 已放置 → 二进制/脚本在 `./tools` 里，可直接调用。
> - ⬜ 未放置 → 有 Windows 版但还没放进来，**不可用**，回退 `recon.py` 或裸 curl/requests。
> - ❌ 不可用 → Linux-only，永不放置，一律跳过。
>
> 用法：把工具二进制放进 `./tools` 后，把对应行的「状态」从 `⬜ 未放置` 改成 `✅ 已放置`。**调用任何工具前先查此表。**

| 工具 | 调用名 | 用途 | 状态 |
|---|---|---|---|
| recon（内置脚本） | `py -3 tools/recon.py <target> [--probe] [--js]` | 被动侦察：crt.sh 子域 + 静态文件 + 已知路径点测 + JS 挖掘 | ✅ 已放置 |
| ffuf | `tools/ffuf.exe` | 目录/参数 fuzz（仅 ROE-AGGRESSIVE） | ⬜ 未放置 |
| httpx | `tools/httpx.exe` | HTTP 探测 / 技术指纹 | ⬜ 未放置 |
| nuclei | `tools/nuclei.exe` | 模板扫描（仅 ROE-AGGRESSIVE） | ⬜ 未放置 |
| subfinder | `tools/subfinder.exe` | 子域被动收集 | ⬜ 未放置 |
| gau | `tools/gau.exe` | 已知 URL 聚合 | ⬜ 未放置 |
| waybackurls | `tools/waybackurls.exe` | Wayback URL | ⬜ 未放置 |
| dnsx | `tools/dnsx.exe` | DNS 批量解析 | ⬜ 未放置 |
| gobuster | `tools/gobuster.exe` | 目录爆破（仅 ROE-AGGRESSIVE） | ⬜ 未放置 |
| trufflehog | `tools/trufflehog.exe` | Git/文件密钥扫描 | ⬜ 未放置 |
| gitleaks | `tools/gitleaks.exe` | Git 密钥扫描 | ⬜ 未放置 |
| massdns | — | raw socket，无 Windows 版 | ❌ 不可用 |
| masscan | — | 网络层发包，Windows 不可靠 | ❌ 不可用 |

## 调用规则

1. 调用任何 CLI 前先看「状态」：✅ 才调；⬜ 或 ❌ → 回退 `py -3 tools/recon.py` 或裸 curl/requests。
2. 即使工具可用，仍受 CLAUDE.md 全局约束管（RoE / 每端点 ≤5 / Safe Payload / No Brute Force）。fuzz/扫描类工具（ffuf/gobuster/nuclei）仅在 `ROE-AGGRESSIVE` 下才允许调用。
3. 计数持久化：Agent 发送请求后照常更新 `./temp/rate-counter.md`。
