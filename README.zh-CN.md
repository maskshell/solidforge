# Solid Forge

[English](README.md) | **简体中文**

*面向 AI 编码代理的循环工程（Loop Engineering）系统——以一个 Claude Code 插件打包提供。*

一个 Claude Code 插件，打包了 **converge → specify → implement**（收敛 → 规格化 → 实现）管线，外加两个可叠加的 **结果轴（outcome-axis）** 层（已引用源核验 + 未引用先例碰撞检测）：`cross-source-review`、`blueprint-crafting`、`parallel-development`、`primary-source-verification`、`prior-art-search` 五个技能、它们的级联子代理，以及确定性收敛环钩子——可整体安装、按项目启用。

## 打包内容

- **技能（Skills）**
  - `parallel-development` — 并行开发编排器，带确定性收敛-修复环：双环门（fast gate + 架构契约门）、状态机断路器、带只读守卫的意图蓝图（Intent Blueprint）、微步快照、黄金路径注册表。支持 Python、Swift、Web/TS、Rust、Java。
  - `blueprint-crafting` — 产出经收敛校验的上游工件（PRD、架构设计、迭代计划、可执行摘要、研究），供 parallel-development 作为权威参考使用。
  - `cross-source-review` — 驱动同源（same-family）+ 异源（different-family）交叉评审，将文档驱动至实质收敛（substantive convergence）；是 blueprint-crafting 上游的收敛层（bc 之前的需求输入、设计文档、wiki 页均可），也可独立复用。其收敛记录内嵌每轮 findings 与逐条处置（可审计——读者可复核每条 finding 及其处理方式）。
  - `primary-source-verification` — 只读、以源为锚的逐条核验器：抽取原子级、可源裁决的 claim，抓取每个被引用的原始源，输出逐条裁决（verified / refuted / narrowed / unverifiable）加诚实覆盖率披露（`oracle_verified_under_known_coverage`）。在结果轴上与 csr 互补——可叠加、**不是顺序管线的一个阶段**；永不输出 `correctness_converged`。**门模式（GATE MODE，2026-08）**：对 rule-13 文档（承重引用 + 可 fetch 源），承重 claim 子集先于 csr 运行，作为廉价 GO/NO-GO 前提检查——门记录明确标记为非权威；csr 之后的全量 M 运行才是唯一权威覆盖率记录。
  - `prior-art-search` — 只读、以搜索为锚的逐新颖性 claim 碰撞检测器：抽取文档的新颖性 claim，对先例语料逐一搜索，输出逐条碰撞裁决（collision / uncited-relevant / clear-under-search / inconclusive）加诚实覆盖率披露（`collisions_under_known_coverage`）。第二条结果轴腿——向后-未引用（psv 是向后-已引用）；可叠加，永不输出 `novel_confirmed`。
- **代理（Agents，22 个，以 `solidforge:<name>` 插件作用域注册）** — architect、backend-developer、frontend-developer、ios-developer、ios-tester、tester、code-reviewer、requirements-manager、devops-engineer、documentation-writer、security-specialist、graphiti-config-generator、playwright-test-planner / -generator / -healer、plan-reviewer、doc-reviewer、claim-extractor、claim-verifier、novelty-claim-extractor、collision-verifier、researcher。按角色的代码模式位于 `parallel-development/references/agent-patterns/`。
- **钩子（Hooks）** — `fast_gate.py`（PostToolUse）、`blueprint_guard.py` + `counters.py`（PreToolUse）。脚本随技能的 `infra/` 目录发布（纯 Python 标准库），从插件根目录运行——它们基于 `$CLAUDE_PROJECT_DIR` 工作，无需逐项目复制脚本。
- **命令（Command）** — `/solidforge:arm-tools`。

### 技能文档（`docs/`）——维护者向的设计依据

每个技能的 `docs/` 目录包含设计提案、迭代计划、ADR 日志（`design-decisions.md`）与收敛记录（`*.convergence.md`）。这些是**维护者向**的设计依据（技能为何如此工作、经过了怎样的交叉评审、锁定了哪些决策）——不是用户向文档。**使用技能只需要 `SKILL.md` + `references/`**。`docs/` 保持公开是为了透明：它们是支撑每个设计决策的收敛轨迹，与项目自身的收敛驱动哲学一致。

## 安装 + 启用（第 1 层）

本地开发（无市场）：

```bash
claude --plugin-dir /path/to/solidforge
```

或通过市场 / `--plugin-url`（zip）。然后按项目启用（`/plugin`）或全局启用。
启用会激活技能、作用域代理与钩子。插件代理优先级为 5——用户 `~/.claude/agents/` 下同名全局代理优先，因此技能按作用域名（`solidforge:<name>`）生成插件代理。

## 武装项目（第 2 层）

插件不修改宿主项目的构建文件，因此启用**不会**预置门工具或架构配置。在目标项目中运行：

```cli
/solidforge:arm-tools            # 预置架构配置 + 宪法 + 模板 + 门状态
/solidforge:arm-tools --with-tools   # 同时把匹配版本的门工具加入项目 dev 依赖
```

这会复制各语言架构配置（`.importlinter.ini`、`.dependency-cruiser.cjs`、`.swiftlint.yml`、`clippy.toml`、`checkstyle.xml`），把 L1 宪法 + 门工具链说明追加到项目 `CLAUDE.md`，复制意图蓝图模板，并为循环的运行时状态添加 `.gitignore` 条目。`--with-tools` 把门工具加入项目自己的 dev 依赖（uv/poetry/pip/npm/pnpm/yarn）；仅系统级工具会打印安装命令。可逆：`arm.py --revert`（dry-run；`--apply` 执行）。

参见 `parallel-development/references/install.md`。

前端项目需要设计治理？在同一项目中同时武装 Impeccable：`npx impeccable install` 然后 `/impeccable init`（配套插件，不打包——见下）。

## 配套插件（推荐，不打包）

Solid Forge 不重复实现已有官方维护插件（`claude-plugins-official`）的能力：

- **代码智能（LSP）** — `arm-tools` 按检测到的语言推荐对应的官方 LSP 插件（`pyright-lsp`、`rust-analyzer-lsp`、`swift-lsp`、`jdtls-lsp`、`typescript-lsp`）加语言服务器二进制。非强制声明——按语言选择启用。
- **安全** — `security-guidance` 补充 Solid Forge 自己的 `arch_contract_deps` 门（循环内的密钥 + 依赖漏洞），提供会话级持续审查。
- **开发工作流** — `commit-commands` 与 `pr-review-toolkit` 是叠加配套（Solid Forge 有自己的提交策略，经由 `loop_state.py init --commit` 和 `code-reviewer` 代理）。
- **前端设计治理 — Impeccable**（`pbakaus/impeccable`，`claude-plugins-official`）。
  对前端项目，武装它（`npx impeccable install`，再 `/impeccable init` 写 DESIGN.md/PRODUCT.md），收敛环会集成它：Impeccable 的 44 条规则检测器成为设计保真门（每次编辑的咨询性 finding + 收敛扫描），其 `DESIGN.md` 成为实现者据此编码的冻结设计锚点，`/impeccable critique` 增强外环评审。
  像素级精确团队可选择在视觉漂移时硬回滚。
  参见 `parallel-development/references/external-skills.md`。
- **API 契约治理 — Spectral**（`@stoplight/spectral-cli`）。
  对有 OpenAPI/Swagger 规范的项目，武装它（`brew install spectral-cli` 或 `npm i -g @stoplight/spectral-cli`），收敛环会集成它：`spectral_adapter.py` 成为 API 规则集门（按 `spectral:oas` + `.spectral.yaml` 对规范做咨询性收敛扫描），与 `arch_contract_api.py`（存在性/路径检查）互补。深度 2：规范冻结为实现者据此编码的 Phase-0 锚点。
  参见 `parallel-development/references/external-skills.md`。
- **源码 SAST — Semgrep**（`semgrep`）。
  武装它（`brew install semgrep` 或 `pip install semgrep`），收敛环会集成它：`semgrep_adapter.py` 成为源码 SAST 门（对源码做 CVE 模式咨询性收敛扫描——OWASP Top 10、注入、路径穿越、弱加密——经 `.semgrep/` 或 `--config auto`），与 `/security-review`（LLM）和 `arch_contract_deps`（密钥 + 依赖 CVE）互补。finding 为咨询性（SAST 易误报）。
  参见 `parallel-development/references/external-skills.md`。
- **文档措辞治理 — Vale**（`vale`）。
  武装它（`brew install vale` / GitHub release），配合提交的 `.vale.ini` + `styles/`，收敛环会集成它：`vale_adapter.py` 成为措辞质量门（对文档做术语/语气/拼写/包容性的咨询性收敛扫描）。补齐文档-质量轴的缺口——blueprint-crafting 检查上游文档结构、语言架构门检查代码，但两者都不检查措辞。
  参见 `parallel-development/references/external-skills.md`。
- **API 破坏性变更检测 — oasdiff**（`oasdiff`）。
  武装它（`brew install oasdiff`），收敛环会集成它：`oasdiff_adapter.py` 成为向后兼容门（把每个受跟踪的 OpenAPI 规范与其 git HEAD 版本做咨询性 diff——删除必填字段、类型变更、删除端点）。与 Spectral（规范风格）和 `arch_contract_api`（存在性/路径）互补；两者都不做版本 diff。
  参见 `parallel-development/references/external-skills.md`。
- **依赖许可证合规 — Trivy**（`trivy`）。
  武装它（`brew install trivy`），收敛环会集成它：`license_adapter.py` 成为许可证合规门（从锁文件盘点依赖许可证的咨询性扫描）。与 `arch_contract_deps`（密钥 + 依赖 CVE）互补——法律/合规轴。无项目策略时仅为原始清单；copyleft/兼容性分析保持人工。
  参见 `parallel-development/references/external-skills.md`。
- **IaC 错误配置 — Checkov**（`checkov`）。
  武装它（`brew install checkov` / `pip install checkov`），收敛环会集成它：`iac_adapter.py` 成为基础设施错误配置门（对 Terraform/Kubernetes/Dockerfile 做咨询性扫描——开放存储桶、宽松安全组、特权容器）。面向基础设施项目可选启用（无 IaC 文件时 no-op）；在应用语言平台模型之外。
  参见 `parallel-development/references/external-skills.md`。
- **内置编排 — 动态工作流（`ultracode`）**（Claude Code 内置，非插件）。
  在另一层补充收敛环：收敛环是逐特性的工程收敛（有门 + 有断路器 + 成本可预期）；`ultracode` 工作流（提示词关键字，或 `/effort ultracode`）是脚本驱动的、高 token 编排，面向**未知规模** / 一次性 / 跨切面的工作——仓库级缺陷扫描、大型迁移、交叉核验研究、对抗性多评审小组。**不要用工作流替代收敛环**：其裁决分发是语义模型判断，不是代码路由（ADR #32、#33）。

## MCP 前置（外部服务器，不打包）

由 `parallel-development` 引用（blueprint-crafting 无 MCP 依赖）。不在 `.mcp.json` 中打包——它们是用户自跑的服务器；按需声明：

- **graphiti** — 可选。跨会话记忆 + 黄金路径。不可达时技能优雅降级（跳过记忆操作）。打包的 `graphiti-config-generator` 代理帮助配置。
- **playwright-test** — E2E 必需。为三个 `playwright-test-*` 代理的 `mcp__playwright-test__*` 工具驱动。
- **ast-grep** — 可选。自动化代码评审模式（也可用作 `@ast-grep/cli` CLI，MCP 是两条路径之一）。

## 目录结构

```text
solidforge/                      （仓库根 = 插件根）
  .claude-plugin/plugin.json     manifest（name=solidforge, version, description）
  skills/
    parallel-development/        收敛环实现技能
    blueprint-crafting/          规格侧技能（Intent Blueprint → plan-model）
    cross-source-review/         跨源文档收敛技能（同源 + 异源 → 实质收敛）
    primary-source-verification/ 逐条源核验技能（结果轴；基于 fetch、向后-已引用、可与 csr 叠加）
    prior-art-search/            逐新颖性 claim 先例碰撞技能（结果轴；基于搜索、向后-未引用、可与 csr+psv 叠加）
  agents/                        22 个代理定义（注册为 solidforge:<name>）；按角色代码模式在 skills/parallel-development/references/agent-patterns/
  hooks/hooks.json               PreToolUse + PostToolUse → ${CLAUDE_PLUGIN_ROOT}/skills/.../hooks/*.py
  commands/arm-tools.md          /solidforge:arm-tools（第 2 层）
```

状态：插件以 `solidforge@skills-dir` 加载（仓库根 = 插件根）。技能位于 `skills/` 下；代理注册为 `solidforge:<name>`，派生引用使用作用域形式。
逐项目武装（`enable` + `/solidforge:arm-tools`）是用户侧步骤——见上文「武装项目」。
