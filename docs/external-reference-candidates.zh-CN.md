# 外部参考候选 — 挂账清单（中文版）

> 本文件是 `docs/external-reference-candidates.md` 的衍生翻译。**英文版为权威源**：两版如有分歧，以英文版及其收敛记录 `docs/external-reference-candidates.csr-record.json` 为准；本翻译未单独走 csr 收敛。翻译日期 2026-09-14，对应英文版 csr 3 轮收敛后的状态。
>
> 状态：持续更新的挂账清单（living backlog，2026-09-14 更新）。**不是承诺**。条目来自四轮外部评估（2026-09-14 执行）与一次内部推导（2026-09-14 记录；其第二 run 数据为运营者报告），每条均经过**问题存在性判据**（problem-existence test）筛选：只有当本 workspace 确有某机制所解决的问题时才借鉴，而非因为机制本身漂亮。无任何条目排期；折入（fold-in）只发生在自然触点；任何采纳在实施前先过 ADR（本清单自身政策——比 workspace 规则 6 更严，规则 6 只要求非显然决策记 ADR）。
> 来源：
>
> - E1 — github.com/frontier-harness-eval/eval：skill 分发形态 + 记录溯源纪律。（覆盖披露：四个来源中唯一其归属主张依赖编排者评估期抓取的——repo 树 + SKILL.md + PROMPT.md + cli/index.mjs，2026-09-14——**未**经 web 席位复核；E2/E3/E4 已在 round 3 经 web 席位确认。）
> - E2 — earendil.com/posts/measuring-code-sloppiness/ + SlopCodeBench（arXiv:2603.24755）：廉价的确定性 slop 度量（verbosity / erosion）。
> - E3 — developers.openai.com/blog/eval-skills：skill 评测（带负对照的触发 CSV、JSONL 确定性 grader、rubric 评分层）。
> - E4 — github.com/cursor/plugins cursor-team-kit（18 个 skill）：审查人格密度（由 C8 吸收——人格密度这条可借鉴物就是 C8 的微采纳批次）、skill 作 rubric + 薄 agent（→ C4）、证据生产者/裁决消费者分离（→ C5 + 外部同构记录）。
> - D1 — 内部推导（2026-09-14）：本文记录背后的 csr dogfood run（schema 审计缺陷类滴漏——每轮只发现一个实例而非全量清扫——跨 1→3 轮；round-1 的 Blocker 本身是修复引入的）+ 运营者报告的另一会话 csr run（12 轮；1:1 映射类滴漏至 R12；一条 git pickaxe 可见的修复后回归发现得晚——运营者报告、不可抓取）。该阶梯把既有规则 4/5/2 泛化到审查循环编排层；新语义残余是阶梯 + 降级纪律 + C9 行内定义的「frame 作方法缓存」角色。

## 框架

四轮外部评估的结论相同：workspace 的核心架构已经拥有外部来源所开处方的大部分，且通常更严格。本清单只保留通过了问题存在性判据的残余候选。该判据的结果是三值的，下面的价值形态**就是**这三类结果：

- **补缺**（gap-fill，problem-now）：workspace 今天就有这个问题；条目等待自然触点，无需专门开工。
- **可选项**（option，problem-conditional）：问题只在触发事件发生时才存在；模式留档待触发。
- **登记项**（registration，problem-conditional、复发型）：模式留档；仅当触发条件被证实复发时才采纳。

## 候选

| ID | 候选 | 来源 | 价值形态 | 一句话契约 | 触发条件 / 自然触点 |
| --- | --- | --- | --- | --- | --- |
| C1 | 记录内环境溯源 | E1 | 补缺 | csr convergence-record 在其 rounds[] 内获得逐轮环境指纹（provider+model 目前**只**存在于 csr_progress 事件面——没有任何 record schema 携带环境溯源字段，csr round 1 审计；补 proxy/NO_PROXY 状态、wrapper + Claude Code 版本、轮间可比性注记）；pd run-record 在 outer_verdicts 旁获得逐 fold 指纹（它没有 rounds[]——一条 == 一次 inner→outer 上下文折叠）；环境变更 → 换新 run，永不重贴标签；存量记录的回填（2026-09-15 增补）：原件永不改写——never-relabel 同样约束回溯——重建的溯源（从幸存 run 侧车重建，如事件面携带 provider/model 的 progress.jsonl）落在分析语料旁的独立注记层，不可重建处标注 unknown（honest coverage） | 下次触碰 run-record 或 convergence-record schema |
| C2 | diff 级 slop 密度 advisory 门 | E2（+E4 `deslop`——佐证的是这个问题而非该度量：判断级 persona，无公式） | 补缺 | 逐轮 patch 的 Δverbosity——把 E2 的 verbosity 公式 \|AST-Grep flagged lines ∪ clone lines\|/LOC 施加到本轮 patch 上；重复行由 CLONE 检测产出、冗余行（wordy lines）由 AST-Grep 标记——再加一个 patch 范围的 complexity-mass，基于 E2 的逐函数质量项 mass(f)=CC(f)×√SLOC(f)（E2 本身只把这个项在 CC>10 函数上求和为 erosion 份额、从不对一个 diff 求和——patch 范围化是 C2 自己的扩展、不是 E2 的，2026-09-14 经 web 席位核证；裁决包 + 持久记录：`docs/external-reference-candidates.csr-record.json`，于该 run 收敛时写出）——以 `warning` 发出、永不 Blocker（Goodhart 定律——一旦成为优化目标，度量便不再如实度量；E2 这条警告只针对其 ΔLOC 度量，任何 slop 代理都继承它） | 下次触碰 parallel-development 门层 |
| C3a | 表层触发检查移植到 parallel-development | E3 | 补缺 | 把 blueprint-crafting 的 `trigger_check.py` + `activation.json` 注册表模式镜像到 parallel-development 的 description 表层——便宜：注册表 + 检查器，无需 agent 运行 | 同 C2（门层触碰） |
| C3b | 行为层触发套件 | E3 | 登记项 | should_trigger CSV + 负对照，作为真实 agent 探针运行；探的是 bc ADR #8 的缝（skills/blueprint-crafting/docs/design-decisions.md——ADR 编号按 skill 各自计数、跨库撞号；这一条是"激活表层非确定性路由器"决策），该缝被有意留在外环 | 触发回归抵达外环的证据反复出现 |
| C4 | 审查 agent 的 rubric 单源化 | E4 | 补缺 | 薄化 `agents/*.agent.md`，首条指令加载 skill 侧 rubric 文件作为完整标准 + 降级回退；消除与 skill 文档的两份真相重复（L4 关注点；架构级变更） | 下次 reviewer-prompt 重构；先过 ADR（多一跳加载的成本 vs 单源） |
| C5 | 经验性验证证据目录 | E4（`verify-this`） | 登记项 | claim/timeline/baseline/treatment/diff/verdict.md 目录 schema，用于 A/B 测量主张 | 经验性 A/B 验证需求复发（一次性先例：ADR #54 edition 派生的本机复现） |
| C6 | memory 信心分层 | E4（`workflow-from-chats`） | 登记项 | strong/medium/weak/contradicted 四档；`contradicted` → 写入前先问用户（预期价值低） | 跨会话 memory 冲突复发 |
| C7 | 分发对：PROMPT.md 孪生 + 薄安装器 | E1 | 可选项 | 每 skill 一份人可粘贴的驱动提示词（五个猜不到的事实、编号停止边界）+ 面向非 Claude-Code agent 的 materialize/symlink/doctor/forward 安装器 | 公共仓（maskshell/solidforge）开始服务 codex/cursor 消费者 |
| C8 | reviewer-prompt 微采纳 | E4（其 thermo-nuclear review skill） | 补缺 | 可答辩推定 Blocker 中间档；输出优先级排序 + 反 nit-flooding 规则；findings→remedy-direction 配对；「删除复杂度，而非重排复杂度」判据（四件独立采纳的批次） | 下次触碰 prompt-content-spec / reviewer-prompt（L4 纪律适用：这些是不可编码的语义指导，合法属于外环的 prose） |
| C9 | 审查循环阶梯纪律 | D1（内部 dogfood） | 补缺 | finding 沿 实例 → frame 类 →（普查入工件 \| 门）流动——frame 类 = 循环的常设 frame（每条 fresh 腿收到的 core-claims + 方法清单，是其唯一的暖记忆；即「frame 作方法缓存」）；普查入工件 = 对全类一次性枚举写进文档；门 = 确定性内环检查；首次出现某**可枚举**缺陷类的实例时，在修复时点普查（廉价普查立即做、昂贵普查等第二实例）并把该类加入常设 frame；降级（frame → 门）需**同时**满足复发证明与经济学——期望滴漏成本（跨轮反复再发现的实例）须超过新门的 ~9+ 文件 ripple（workspace 规则 5）；frame 条目降级后退役——无界清单会在 prompt 内重建暖 context 锚定（审查者只顾按清单核对、停止探索）；普查只在类宇宙机械可枚举时进行（假完备比滴漏更糟） | 下次触碰 csr/bc/pd 编排文档（frame 构建 / reviewer-prompt 部分） |

## 已核证的仓库现状主张（authoring 前审计 + csr 轮内复核）

这些主张在本文写作前核查过、并由 csr 腿对照漂移复核；round 1 的轮内增补已就地标注出处：

- `skills/cross-source-review/infra/scripts/csr_progress.py`——progress 事件 schema 必填 `provider`（65、73、84 行）；heartbeat 事件渲染 `model`（261 行）。csr_progress 事件中不存在 proxy/NO_PROXY 状态、wrapper/CC 版本或环境指纹。
- bc run-record schema（`skills/blueprint-crafting/infra/schemas/run-record.schema.json`）在 csr round 1 审计（2026-09-14；持久记录：`docs/external-reference-candidates.csr-record.json`，于该 run 收敛时写出）：对 provider|model|proxy|fingerprint|environment|version 零命中——干净。其余四个被查的 record schema——`skills/cross-source-review/infra/schemas/convergence-record.schema.json`、`skills/parallel-development/infra/schemas/run-record.schema.json`、`skills/primary-source-verification/infra/schemas/coverage-record.schema.json`（psv = primary-source-verification）、`skills/prior-art-search/infra/schemas/collision-record.schema.json`——对原始词集**有**命中，但每次命中都 out-of-sense：pd schema 的 fingerprint 命名字段是**错误**指纹（record 级必填 `top_fingerprints`、其条目由 `fingerprint_count` def 定型——"Top recurring error fingerprints (error-compounding evidence)"；其余命中为 prose：`blueprint_version` 固定的是工件版本、"(step-count proxy)"、"provider-normalized"、"wall-clock confounds provider throughput"）；csr schema 唯一的 `provider` 命中是 description 内的 prose（ADR #41）；psv coverage-record 命中在 `volatile_source` prose（"shell environment state"、"unversioned"）与 verified 计数 description 中的 `model` prose；prior-art-search collision-record 命中在覆盖注记 prose（"the comparison model found no collision"、"found text is model-extracted"）。净结论：任何 record schema 都不存在环境溯源**字段**（"provider" property 在全部 skill schema 中零出现）；provider+model 只活在事件面上（C1 修正后的归属）。
- `skills/blueprint-crafting/infra/test/trigger_check.py` 存在且断言 description 表层（positive coverage、no positive steal、parallel-dev reachable、scope guard），由 `infra/test/activation.json` 数据驱动。其文档化的缝：激活路由终究是模型的调用——不可确定性判定（bc ADR #8，skills/blueprint-crafting/docs/design-decisions.md）。**已记录的修正**：来源评估（E3）曾称"完全不存在触发验证"；在表层这个层面是错的。真实残余缺口是 C3a（parallel-development 无等价表层检查）与 C3b（无行为层探针，属有意设计）。
- `skills/parallel-development/infra/hooks/fast_gate.py`——仅 per-file lint/format（ruff / swift-format / rustfmt / google-java-format / gofmt / web 文件的 eslint、config 门控）；更重的检查归收敛点的 arch-contract 门。门层任何地方都没有重复度/slop 密度信号（C2 缺口主张；最接近的类比 drift_check.py 是规则 7 的样板漂移检查，不是 slop 密度）。
- 审查 agent 位于仓库根 `agents/*.agent.md`——五个对抗性审查席位（doc-reviewer、claim-verifier、plan-reviewer、web-claim-verifier、collision-verifier；claim-verifier 与 collision-verifier 是逐 claim 裁决专用，web-claim-verifier 是双模式——claim 模式出裁决、question 模式出 findings[]——doc-reviewer 与 plan-reviewer 出 findings 列表）——且内嵌各自的审阅标准与输出 schema（C4 前提；抽取器席位 claim-extractor / novelty-claim-extractor 不在类内——它们只枚举、不裁决）。

## 不采纳清单

已评估并否决、附理由——不必重新推导：

- E1 的 Runta 运行时机械（付费云 checkpoint/egress proxy；本 workspace 的环境是仓库 + 本地确定性门）。
- E1 的 benchmark 内容与 vendor onboarding（该 skill 一半是商业引导）。
- E4 的薄 skill Trigger/Workflow/Guardrails/Output 骨架（本 workspace 的渐进披露/加载链体系严格更丰富）。
- 零 eval 发布（E4 以无任何 eval 的状态发布 18 个 skill；本 workspace 的 self-gate 规则 1 禁止这种姿态）。
- TS/npm 中心约定（E4 kit 假设它们；本 workspace 是多语言 + 按平台注册表）。

## 外部同构记录（仅验证，无动作）

记录原因：独立收敛是核心架构没有遗漏某物的证据：

- E1 的 `methodology_comparable: false` 默认不排名 + 永不重贴证据标签 ↔ 规则 3（never silently green）+ psv/prior-art-search 的覆盖披露顶行。
- E2 的 judge 不可靠（呈现线索偏差可翻转裁决）↔ csr 的 fresh-context + schema'd findings + 收敛循环，从不做单遍偏好判定。
- E3 的 prompt→trace→checks→score、确定性先行分层 ↔ fast gate / arch-contract gate / 外环（outer ring）拆分。
- E4 的证据生产者（control-cli/control-ui）喂给裁决消费者（verify-this）↔ csr/psv 的 reviewer-verifier 分席；E4 的 skill 作 rubric + 薄 agent ↔ 本 workspace 的 skill+agent 体系（C4 是差额）；E4 的 `verify-this` 三值裁决带混淆变量规则 ↔ psv 的 verified/refuted/narrowed/unverifiable。

## 判定规则

条目离开本清单只有三条路：在自然触点经 ADR 采纳（补缺）、触发事件发生（可选项）、触发条件被证实复发（登记项）。离场时按问题存在性判据重筛——问题此后已在库内解决的候选（如 C3 的原始形态）应收窄或撤销，而非按原样实施。
