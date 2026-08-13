# Solid Forge — 用户指南

[English](USER_GUIDE.md) | **简体中文**

面向 AI 编码代理的循环工程系统。「完成」意味着工作通过了确定性内环**且** AI 外环——而不是「代理停下来了」。本指南 30 秒交付代码，然后逐层展开 *为什么*（成熟度模型）+ 可选扩展。总览：[README.md](README.md)；安装与功能文档：[install.md](skills/parallel-development/references/install.md)；成熟度框架：[maturity.md](skills/parallel-development/references/maturity.md)（自包含）。

## 30 秒上手

有编码任务？直接调用 pd——**斜杠命令保证技能激活**（无路由意外）：

> /parallel-development implement a FastAPI endpoint for user registration

**`/parallel-development`**（pd）运行收敛环（lint → 架构契约 → 供应链 → 测试 → AI 评审），迭代至双环皆净，每个收敛阶段在特性分支上提交（永不 `main`），然后汇报。你不直接调用代理或钩子——技能负责编排。（规格化半边是 **`/blueprint-crafting`**，bc。）裸表述 `implement …` *通常*也会路由到 pd——但显式斜杠命令是 100% 路径；需要确定性时用它。

单任务无需计划。已有计划则跳到 [工作流](#工作流)。

## 技能管线

五个技能，一条管线加两个可叠加结果轴层（已引用源核验 + 未引用先例碰撞）：

| 技能 | 职责 | 触发 |
| --- | --- | --- |
| **cross-source-review**（csr） | 收敛——驱动同源 + 异源交叉评审，将文档驱动至实质收敛 | "cross-review this requirements doc"、"converge this design doc"、"different-family review this wiki page" |
| **blueprint-crafting**（bc） | 规格化——收敛的规范、架构设计、迭代计划 | "author a spec for …"、"author an arch-design for …" |
| **parallel-development**（pd） | 实现——代码经双环收敛 | "implement …"、"fix …"、"refactor …" |
| **primary-source-verification**（psv） | 核验——逐条已引用源核验（可叠加结果轴层，非顺序；门模式：rule-13 条件成立时，承重子集 GO/NO-GO 先于 csr） | "verify this doc's citations against primary sources"、"fact-check this spec's arXiv claims" |
| **prior-art-search** | 碰撞检测——为文档的新颖性 claim 搜寻未引用先例（可叠加结果轴层） | "does this paper overclaim novelty"、"hunt uncited prior art for these novelty claims"、"is this framing already in the literature" |

```text
csr（收敛文档）→ bc（规格化）→ 冻结规范 → pd（实现）→ 收敛代码
psv（逐条核验已引用 claim vs 其 fetched 源）——可叠加结果轴层；csr 之后的全量 M 记录为权威
psv-gate（承重子集，GO/NO-GO）——可选，rule-13 条件成立时在 csr 之前；门记录不是覆盖率记录
prior-art-search（为每条 NOVELTY claim 搜寻未引用先例）——第二条可叠加结果轴层
```

psv 与 prior-art-search 是两条结果轴腿——都可叠加，都可在任意文档上运行，在 csr 之后或旁边。psv 另有**门模式**：rule-13 条件成立时（承重引用 + 可 fetch 源），以承重 claim 子集**先于 csr** 运行——门的 GO/NO-GO 是批次信号，**不是**覆盖率记录；权威覆盖率披露只来自 csr 之后的全量 M 运行。psv = 向后-已引用（每个被引源是否真的支持该 claim？）；prior-art-search = 向后-未引用（可找到的先例是否已提出文档未引用的新颖性 claim？）。二者可组合（高风险文档可两者都跑）；永不合并；两者都不输出真值/新颖性布尔（`oracle_verified_under_known_coverage` / `collisions_under_known_coverage`；永不 `correctness_converged` / `novel_confirmed`）。

csr 是 **bc 上游**的收敛层（也可独立复用）：它驱动同源（fresh-context）+ 异源（different-family，跨族，如 DeepSeek）多轮评审，把文档类工件——bc 之前的需求输入、设计文档、wiki 页——驱动至**实质收敛**（核心 claim 覆盖核验 AND 连续 ≥2 轮无新 Blocker；注意：收敛不是「零 finding」）。bc 可对草案调用 csr 做异源一轮。csr 不是代码评审（pd）、规格创作（bc）或研究收集（bc 的 researcher）；它收敛**过程轴**质量（结构良好、内部一致、引用准确），绝不裁决文档是否「正确」（结果轴——人工）。其收敛记录可审计：每轮内嵌经调和的 findings + 逐条处置（发现了什么、做了什么处理）。配置与自定义提供方：[csr install.md](skills/cross-source-review/references/install.md)。

激活按描述进行（模型从你的措辞路由）——通常正确，但可靠性重要时请显式调用：`/cross-source-review`、`/blueprint-crafting`、`/parallel-development`、`/primary-source-verification`、`/prior-art-search`。

> **bc 负责形式化；*正确*的需求由你来挖。** bc 按*约束画像*（结构 / 锚点 / 权威链）收敛工件——那是**过程轴「质量达标」**（符合输出规范——规范结构良好）。它**不负责**规范是否捕获你的*真实*需求——那是**结果轴**（仅人工；每条 run-record 上的 `rightness: human_confirm_required`；[bc SKILL.md](skills/blueprint-crafting/SKILL.md)）。「质量达标」≠「满足真实需求」。
>
> 因此裸 `author a spec for X`（如「写个 POS 规范」）产出的是**建立在 bc 自身假设上的结构良好规范**，而非你的需求。先挖出需求——对话、既有文档、或 bc 对可研究部分的研究——**然后** bc 把它们收敛成 pd 实现的冻结工件。bc 负责收敛；**你负责结果**。（`research …` **不是**独立的 bc 触发：研究的价值是*真*——那是 bc 不负责的结果；bc 把研究当作**创作输入**，喂给它所收敛的工件，但发现的真伪由你核验。）

> **csr 收敛文档；正确内容仍是你的。** `/cross-source-review`（csr）经同源 + 异源交叉评审把文档驱动到*实质收敛*——过程轴（结构良好、内部一致、引用准确）。与 bc 一样，它**不负责**文档是否捕获你的真实需求（结果轴，人工）。在 bc 形式化**之前**用它收敛需求/设计文档，或对任何需要跨源对抗评审的文档独立使用（wiki 页、设计文档）。

### 双轴文档收敛：csr + psv（可选——面向高风险、引用密集文档）

psv 是**可选且可叠加**的，不是必需阶段。仅对**高风险、引用密集、错引会实质上削弱论证**的文档使用（引用 arXiv 的规范/研究、引用标准的设计文档）。这些条件成立时跑**两次**：先于 csr 的承重 claim **门**（GO/NO-GO——门的 GO 是批次信号，不是覆盖率记录），然后 csr 之后的全量 M 权威运行。判别器（ODP-5，2026-08-10）：门在**承重引用以外部源为主**（arXiv/博客/标准——模型 recall 盲区带）且**长档**（LONG-tier，预期 csr 投资 ≥ 3 轮）的文档上有价值；以本地文件引用为主的文档——csr 单独充分；短文档永不划算（门成本 ≈1.5 轮 vs 最多省 2 轮）。低引用或低风险文档，csr 单独充分（psv 返回 `M=0 → no admissible surface`）。

使用时分两趟——先于 csr 的承重 claim **门**（GO/NO-GO；其承重清单成为 csr 的核心 claim 框架），然后 csr 之后、bc 之前的权威全量 M 运行：

1. **`/cross-source-review`** — 过程轴：结构良好、内部一致、引用结构化、覆盖完整（recall 基）。
2. **`/primary-source-verification`** — 结果轴可裁决面：每条引用 claim 对其 **fetched** 源核验（`verified` / `refuted` / `narrowed` / `unverifiable`）+ 诚实 `oracle_verified_under_known_coverage` 披露（fetch 基）。

**顺序（rule-13 文档）：`psv(gate) → csr → psv(full M) → bc`**——门先行（廉价前提检查；NO-GO → 在 csr 投资前返工源），全量 M 在 csr 后（权威）。非 rule-13 文档：`csr → psv → bc` 不变（psv 为可选插入，非固定管线阶段）。psv 抓到 csr recall 基腿会漏的引用张冠李戴（它以此方式在同类技能的设计文档里发现过真实缺陷）；csr 抓 psv 抓不到的结构缺口。psv 的 finding 回喂 csr 再收敛。两者都不裁决文档是否 *正确*——那保持人工。

**另一条结果轴层 — `/prior-art-search`：** psv 检查文档的*已引用*源，prior-art-search 则为文档的**新颖性** claim（"we introduce X"、"first to Y"、"no prior art"）搜寻*未引用*先例。用于新颖性框架可能过度主张的高风险文档——设计论文、研究文档——与 psv 并行或替代。prior-art-search 输出 `collisions_under_known_coverage`（N 碰撞 / U 未引用相关 / C 搜索内清晰 / I 不确定，of M），永不输出 `novel_confirmed`（证据缺失极限：零碰撞结果是「所搜范围内无碰撞」，不是「新颖」）。其 oracle——可搜索的先例语料——在两层上弱于 psv 的 fetched 源（比较侧 + 选择侧），这正是它止步于覆盖率披露的原因。

## 工作流

### 从已有计划实现

把任何计划形状的文档交给它——手写的、Cursor 的 `.plan.md`、架构师的产出：

> /parallel-development implement feature X per @my-plan.md

pd 读取它，向你展示工作队列（条目、依赖图、DoD 来源）供确认，然后逐条串联到收敛。你得到收敛代码加两件工件：打印到 stdout 的逐条结果摘要（`plan_queue.py aggregate`），以及 `.claude/parallel-dev/runs/<task>-<stamp>.json` 的 run-record（包含步骤、预算与 `l4_assessment`；gitignored；恢复 + 审计记录）。

### 先规格化，再实现（完整管线）

想要端到端做对？**先挖需求**（bc 形式化；它不发现——见[上文提示](#技能管线)），然后规格化，再按冻结规范实现：

1. **挖需求** — 交互对话、既有需求/上下文文档、或 bc 对可研究部分的研究（多源 web 收集）。这是*结果轴*步骤；*正确*的需求是你的。裸 `author a spec for X` 跳过此步，让 bc 生成貌似合理但假设的内容。
2. `/blueprint-crafting author a spec for feature X`（+ 挖出的上下文）→ bc 收敛并冻结规范——*过程轴*步骤：把你的需求塑造成结构化、锚点完整、权威一致的工件。
3. `/parallel-development implement feature X per the spec @frozen/feature-x.queue.md` → pd 检测 bc 来源并走**富路径**：bc 已解决的决策与研究前向流动（pd 不会重问或重想），规范的验收标准播种可执行测试。「规格了什么」与「构建了什么」之间无空隙——但规范只反映步骤 1 挖出的内容。

### 把文档交叉评审到收敛（csr）

有文档——需求输入、设计文档、wiki 页——需要对抗性交叉评审后才敢信它？`/cross-source-review`（csr）驱动同源 + 异源多轮评审到**实质收敛**：

> /cross-source-review converge this requirements doc @reqs.md

csr 交替同源腿（`solidforge:doc-reviewer`，fresh-context，只读）+ 异源腿（DeepSeek 经 `hetero_doc_review.py`），各喂对方 findings 以追捕缺口（而非重复陈述），直到核心 claim 覆盖核验 AND 连续 ≥2 轮无新 Blocker。触顶 → `adversarial-stalemate`，升级给你（永不静默选边）。你得到收敛文档 + 诚实收敛记录（过程轴裁决；结果保持人工）。

**武装——基于环境变量，无 arm 命令。** csr 的门是自门（它们在 csr 自己的基础设施上跑，不在你的项目上），所以你的项目无需安装任何东西——只需异源腿的提供方 token：`export DEEPSEEK_ANTHROPIC_AUTH_TOKEN=sk-...`（或项目 `.env`）。同源腿无需任何东西。自定义提供方 + token 变量命名规则：[csr install.md](skills/cross-source-review/references/install.md)。

**带交叉评审的完整管线**：挖需求 → `/cross-source-review converge @reqs.md` → `/blueprint-crafting author a spec …` → `/parallel-development implement …`。csr 可选——bc 形式化你交给它的任何输入，收敛与否；csr 先提升输入质量。

### 一次性 bc → pd（跳过规范的人工评审）

可以在一条提示里串联两个技能——bc 产规范、pd 消费，**中间无人评审规范**：

> Using @context.md, have `/blueprint-crafting` produce a spec, then `/parallel-development` implement it
>
> （中文同样：`针对 @xxx.md，使用 /blueprint-crafting 输出规范给 /parallel-development 完成迭代`）

**权衡——你在跳过结果轴评审。** bc 的规范是过程轴收敛的（结构良好），**不是**结果轴验证的（可能反映 bc 的假设，而非你的真实需求——见[上文提示](#技能管线)）。没有 bc 与 pd 之间的人工评审，bc 的假设会直接进入代码。当 `@context.md` 已携带真实需求时**风险较低**（bc 形式化已知良好的输入——尽管 bc 仍是生成模型，可能误读良好输入，残余风险仍在）；需求模糊、需要 bc 去发现时**不适合**（它不能——bc 形式化并研究可研究部分，但你的*真实*需求在其上游）。高风险工作保留上面的三步流程并评审。

### pd 日常任务

都跑同一个收敛环，单条目：

| 你想 | 提示 |
| --- | --- |
| 修 bug | `fix the bug in auth/login.ts where …` |
| 重构 | `refactor the payment module to use …` |
| 测试 | `write e2e tests for the checkout flow` |
| 刚写完代码的文档 | `document the API I just implemented` |

**提示**：若你的规范或工件是中文，bc 的锚点检测是双语的（英文 + 中文关键字）——无需变通。

## 为什么有效——成熟度模型

这是「为什么」。决定代理能否长时间无人值守运行的杠杆是**系统级流控制**，而非更聪明的提示——单步质量已近饱和，但长任务的总通过率是每步可靠性的*乘积*（~95% 每步 × 五十步跌破 8%）。Solid Forge 的价值在于系统性地防御让长代理运行失败的长程**劣化效应**，按 **L1–L4 成熟度阶梯**（*内在流控制轴*）分级。完整框架 + 自评：[maturity.md](skills/parallel-development/references/maturity.md)。

### 四种劣化效应（长运行死于什么）

| 劣化 | 发生了什么 | 成熟防御 | 在 Solid Forge 中 |
| --- | --- | --- | --- |
| **上下文腐烂（Context Rot）** | 冗余思考 + 冗长工具输出（千行日志）填满窗口；代理遗忘 + 后期劣化。注意力呈 U 形——中间内容使用最少。 | 层级转换时显式剪枝 + 状态摘要折叠。 | 内环→外环转换处的上下文折叠——只有一句话折叠摘要 + diff + 蓝图跨环，绝无内环 stderr 痕迹。 |
| **错误复合（Error Compounding）** | 微小逐步偏差（错文件、失败正则、幻觉路径）沿步骤链指数放大。 | 结构化自纠 + 独立反思遍（诊断 ≠ 修复）。 | 双环自纠：fast gate PostToolUse `decision:block` → 下轮自修；结构化越权日志；独立外环评审者是第二遍反思。 |
| **目标漂移（Goal Drift）** | 大型跨模块任务中代理被拉入子问题、忘记全局目标。 | 外部只读意图锚点 + 周期性对原 diff。 | 冻结意图蓝图（三层只读）+ diff-to-blueprint → intent-drift 裁决 → 硬回滚 + 反向提示注入。 |
| **规格博弈（Specification Gaming）** *（正交——见下）* | 代理优化的是替代规格（proxy spec，如「过了测试」、类型检查、自评），而非真实目标——静默语义失败。代理/真实目标间隙**不可约**（规格问题）。**关键张力**：L4 的「主动测试自验证」是*同源*——这种劣化的**载体**，而非防御。 | 一个**异源 oracle**（盲点集不同的外部源：生产回归、形式规范、人类语义门、不同的模型族）。 | 异源扩展（部分）——不同模型族；公开博弈（删/弱化测试）也被 AC→test-name 门捕获。 |

前三者是概率生成 + 有界注意力在长序列上的*物理*后果。第四者是**关系**失败（代理 ≠ 真实目标）——与流控制正交；它**不**推进 L1–L4。

### L1–L4 阶梯（内在流控制轴）

| 等级 | 流控制特征（防御的劣化） | 交付物 | 运行视界 |
| --- | --- | --- | --- |
| **L1 单轮** | 无环、无状态——由显式用户回合驱动。 | 单函数生成、语法修复。 | 1 步 |
| **L2 固定环** | ReAct 环但流控制硬编码；无异常处理 → 意外错误死环或中止。*（错误复合未防御。）* | 单文件 bug 修复、清晰上下文中的简单特性。 | 单步到数十步 |
| **L3 状态路由** | 提示 = 状态机控制语言；结构化异常处理 + 降级（测试失败 → 反思模板）。错误复合部分防御。 | 多文件重构、小型独立模块、初始 TDD。 | 数十步 |
| **L4 自主闭环** | 深度运行时绑定：主动生成测试自验证、为 token 效率剪枝记忆、锚定意图防漂移、**外部状态机经断路器强制收敛**。**三种物理劣化系统性防御**（规格博弈正交——自测携带它，不防御它）。 | 多文件缺陷修复或闭环特性，在 3 劣化防御下收敛。 | 数百步 |

转换：**L2→L3** 是*硬编码流控制 → 状态机流控制*；**L3→L4** 是*被动异常处理 → 主动运行时治理 + 自验证*。**L4 是内在轴的终点**——「更强的代理」无法跨越它（下述自证悖论）。**没有 L5**：下一个杠杆（异源）在正交轴上，不是更高等级（见下）。运行视界是观测区间估计（以提供方归一化的*步*计，非墙钟），非权威阈值。

### 能力 vs 需求（勿混）

- **能力**（等级所测）= 3 劣化防御下的收敛。与需求无关——熟悉代码库上的自编辑即可佐证它。
- **需求** = 任务模糊度 / 代码库新颖度 / 难度 / 运行视界。高需求运行**压力测试**能力；它**不定义**能力。按难度定义等级是循环论证（「L4 = 能做需要 L4 的任务」）。

### 正交轴——验证源解耦（异源）

规格博弈不是靠爬 L1–L4 防御的，而是沿**第二条、正交的轴**：从**同源**验证（代理自己的测试——与编码者共享盲点）到**异源 oracle**（盲点集不同的外部源）。这**不是 L5**——给它编号会伪装成同轴进展；它是不同种类的杠杆。**自证悖论**：用自己测试验证自己的代理是自证的——验证者与被验证者共享盲点，更强的代理仍抓不到规格博弈。oracle 必须是外部的。

两种失败形态，两种防御：

- **公开博弈**（删失败测试、`@Ignore`、硬编码绕过、收缩测试集）——代理内部结构纪律可捕获：AC→test-name 门 Block 裸删；intent-drift → 硬回滚。
- **隐蔽代理优化**（过拟合 fixture、吞异常、mock 依赖）——结构纪律*无法*捕获；只有异源 oracle 能。

Solid Forge 接入了**部分**异源 oracle（下方可选异源扩展）——跨族对抗评审。部分，因为商业模型族共享训练数据/RLHF 重叠；完全防御需要生产回归 / 形式规范 / 人类语义门（未来）。

### 给自家运行定级

架构具备每个 L4 机制——强制收敛的外部状态机（钩子 + 断路器）、上下文折叠、冻结意图锚点、TDD 默认。但**你的运行的运营等级由你观测，不由我们替你主张**：取决于你的 LLM（不同模型不同）、你如何武装项目、以及你任务的需求。每次运行输出带 `l4_assessment` 块的 run-record——由该运行证据计算的临时裁决（`l4-evidenced` / `not-yet` / `not-a-probe` / `inconclusive`）；读它判断你的设置处于何处。什么塑造等级：

1. **两个不同的杠杆——启用 vs 武装。**
   - **启用插件**（第 1 层）= L3→L4 杠杆。不启用时，技能仅方法论运行（代理跟随 SKILL.md、手动跑门——咨询性，~L3）。启用后，钩子 + 断路器在项目每次编辑时触发——这种外部强制就是 L4 特征。（钩子对所有编辑触发，不仅 `/parallel-development`。）
   - **武装项目**（第 2 层，`/solidforge:arm-tools`）= **实质**杠杆。它预置门实际触发所需：架构配置（规则）+ 门 dev 依赖（引擎）。关键组合是 `--with-tools`——见[武装](#武装项目-solidforgearm-tools)的完整旗标表。有规则无引擎（或反之）→ 工具门降级为覆盖率注记；状态机强制仍运行。绝不静默绿。
2. **异源防御是部分的**（上文）。变异测试（最终的引擎级异源）仍是未来。
3. **断言质量是剩余缺口。** 测试*存在性* + 执行*覆盖率*有防御；断言*充分性*（测试真能抓 bug 吗？）没有——变异测试是最终 oracle。
4. **默认上限位于 L3/L4 接缝**（`cap_M=8` 内环迭代、`time_cap_W=1800s`）——即使设计视界也跨线。提供方无关的**能力**极限是**步上限**（`step_cap_S=200` 工作单元）；token 预算是近似值（钩子读不到真实用量），时间是成本/挂起守卫（墙钟混淆提供方吞吐）——**两者都不是能力信号**。
5. **门覆盖跨语言不均**（Rust/Java 较薄；Go 强）。薄门经 `coverage` 注记诚实降级。

（作者自己的模型 + 代码库特定自评——13 条注意——在 [maturity.md](skills/parallel-development/references/maturity.md)；供参考。你的情况因 LLM + 项目而异。）

## 武装项目（`/solidforge:arm-tools`）

第 2 层设置——预置门 + 可选扩展所需的项目侧文件（门的**实质**，非强制——那是第 1 层，[启用插件](#给自家运行定级)）。幂等（可安全重跑）+ 永不覆盖你现有文件。`<project>` 默认当前项目。

| 调用 | 预置什么 | 默认？ |
| --- | --- | --- |
| `/solidforge:arm-tools`（无旗标） | • 各语言架构契约配置——**仅检测到的语言**（`.importlinter.ini` Python · `.dependency-cruiser.cjs` Web/TS · `.swiftlint.yml` Swift · `clippy.toml` Rust · `checkstyle.xml` Java · `.golangci.yml` Go；递归检测——嵌套 `frontend/`/`backend/` 标记计入）<br>• 意图蓝图模板 → `docs/intent-blueprints/_templates/`<br>• L1 宪法追加到 `CLAUDE.md`（若缺失）<br>• `.env.solidforge.example`（异源密钥占位——命名空间隔离，无真实 token）<br>• `.gitignore` 条目（`loop-state.json`、`runs/`、`.env`、`.env.solidforge`）<br>• LSP + 门状态报告（咨询性；不安装语言服务器） | **是——默认武装** |
| `--with-tools` | 同时把门 dev 依赖加入项目**自己的**包管理器（ruff、import-linter 等——项目本地，无全局安装）+ 门工具链注记加入 `CLAUDE.md` | 可选 |
| `--with-tools --lang <python\|web\|rust\|swift\|java\|go>` | 把 `--with-tools` 限制到**一个**生态系统（多语言仓库只要一种语言的门工具） | 可选修饰 |
| `--scaffold-configs [vale,semgrep,spectral]` | 同时复制外部工具配置模板（`.vale.ini` / `.semgrep.yml` / `.spectral.yaml`）；裸旗标 = 三者全要；若 `vale` 已 scaffold 且在 `$PATH` 则运行 `vale sync` | 可选 |
| `--revert [--apply]` | 移除武装添加的内容——仅限仍与模板逐字节匹配的文件（你的编辑**保留** + 警告）。默认 DRY-RUN；`--apply` 执行。与 `--with-tools` 互斥。 | 逆操作 |

注意：

- **最关键组合**：`/solidforge:arm-tools --with-tools`——默认武装给规则（架构配置）；`--with-tools` 给引擎（门 dev 依赖）。第一方门（fast-gate、arch-contract、supply-chain、test）要真正触发两者都需要。项目已有门工具时（如 `pyproject.toml` 里已有 ruff），裸 `/solidforge:arm-tools`（仅规则）即可。
- `--scaffold-configs` 只 scaffold **Vale / Semgrep / Spectral**。Checkov / OASDiff / Trivy 的武装方式是自行安装工具 + 写配置（门自动检测）。
- 插件更新后重跑 `/solidforge:arm-tools` 以重预置架构配置 / 宪法 / 模板（技能文本变了时；你的编辑保留）。
- 异源扩展的 `.env.solidforge.example` 由默认武装预置；`cp` 为 `.env.solidforge` + 填 token 以启用异源（见[异源](#异源different-family对抗评审正交轴杠杆)）。
- 完整权威列表：[install.md](skills/parallel-development/references/install.md) 第 2 层。

## 可选扩展（随时采纳）

这些是**横切能力**，不是任何阶梯的梯级——按需添加，任意顺序；无一是等级的必备条件。外部工具门是 `warning` 级咨询（浮出 finding，不阻塞收敛）；Impeccable 增加每编辑咨询检测器 + 收敛扫描；异源是**外环**对抗评审，其 finding 喂调和（非仅咨询）。

### 外部工具（Vale / Semgrep / Spectral / …）

1. 安装工具（`brew install vale` / `pip install semgrep` / `npm i -g @stoplight/spectral-cli` / …）。
2. Scaffold 起始配置（或自写）：`/solidforge:arm-tools --scaffold-configs [vale,semgrep,spectral]`——裸旗标 = 三者全要；当 `vale` 已 scaffold **且 `vale` 在 `$PATH`** 时，武装还会运行 `vale sync` 拉取风格包（无它们则 Vale 门 no-op）。
3. `/solidforge:arm-tools` 预置其余（架构配置、宪法、模板）。

然后照常 `implement …`——环检测已提交配置并运行该工具的门。所有外部门都是**咨询性**的；是否升级由你决定。

| 工具 | 门控什么 |
| --- | --- |
| Vale | 文档措辞（术语、语气、拼写、包容性） |
| Spectral | OpenAPI 规范 lint（风格 + 最佳实践） |
| Semgrep | 源码 SAST（OWASP Top 10、注入、弱加密） |
| Checkov | IaC 错误配置（开放存储桶、特权容器） |
| OASDiff | API 破坏性变更检测 |
| Trivy | 依赖许可证合规清单 |

缺席的工具以覆盖率注记跳过——绝不静默通过。`--scaffold-configs` 只 scaffold **前三个**（Vale / Semgrep / Spectral）；Checkov / OASDiff / Trivy 的武装方式是自行安装工具 + 写配置（门自动检测）。

### 带设计治理的前端（Impeccable）

1. 一次性：`/impeccable init` → 编写 `DESIGN.md`（设计 token、组件清单、a11y 目标）。
2. 然后或 `author a spec for the checkout page, referencing @DESIGN.md`（bc 将 DESIGN.md 视为权威链条目），**或** `implement the checkout page`（pd 的意图蓝图携带指向 DESIGN.md 的 `visual_ref`；其 token 流入 NFR + 视觉验收标准）。
3. 或两者串联：`DESIGN.md` → 规范（bc）→ 实现（pd）。

代码同时通过收敛门**和** Impeccable 的设计保真检查。

### 异源（different-family）对抗评审（正交轴杠杆）

*为什么*见上方[正交轴](#正交轴——验证源解耦异源)——跨族第二意见防御同源评审抓不到的规格博弈劣化。*怎么做*：

1. 武装项目：`/solidforge:arm-tools` 复制 `.env.solidforge.example`（命名空间占位——永不与你自己的 `.env.example` 冲突）。
2. `cp .env.solidforge.example .env.solidforge` + 填你需要的 token，如 `DEEPSEEK_ANTHROPIC_AUTH_TOKEN=sk-...`。变量名是约定：`<大写提供方>_ANTHROPIC_AUTH_TOKEN`（匹配 `profiles/<provider>.json`）。
3. 运行一次性对抗评审，或把计划条目标为 `hetero: on` 让 pd 逐条加入（`<plugin-root>` 是 Solid Forge 插件安装处——经 `/plugin` 或插件配置找到）：

```bash
python3 <plugin-root>/skills/parallel-development/infra/scripts/hetero_review.py \
  --diff <file-or-ref> --blueprint <blueprint-ref>
```

省略 `--profile`——wrapper 从 `HETERO_PROFILE`（`<project>/.env.solidforge` / 环境变量，逗号列表 = 双异源，默认 deepseek）解析提供方；硬编码 `--profile` 会静默丢弃所有其他已配置提供方（ADR #48/#5）。

调和：双方都报 → 高置信采纳；仅同源 → 采纳；**仅异源 → 强信号，升级**；都无 → 通过。上面的一次性命令是一趟异源腿；**多轮辩论由编排器驱动**（编排器交替同源 ↔ 异源腿，经 `loop_state` 计轮）。触顶未收敛的辩论由编排器记为 `adversarial-stalemate`（经 `loop_state`）并升级给你——绝不静默选边。**无代码变更添加提供方**：放 `profiles/<name>.json` + 设 `<大写名>_ANTHROPIC_AUTH_TOKEN`。**双异源**：`--profile deepseek,qwen3`。决策锚点：ADR #40；策略：[model-routing.md](skills/parallel-development/references/model-routing.md)。

## 内部机制（好奇时阅读）

**收敛环，简述。** 每个条目运行至双环皆净：

- **内环**（确定性）：**fast gate**（lint/format；format 失败阻塞时采用提交分层补救——纯格式变更隔离为独立 `style:` 提交，逻辑 diff 保持可审）是 PostToolUse 钩子，**每次编辑**触发；在**内环收敛点**，架构契约门（分层 / 依赖 / 并发）→ 供应链门（泄露密钥 + 依赖漏洞）→ 测试门（失败测试 + AC→test-name 映射 + 覆盖率）→ API 契约门（前端↔后端，混合仓库）各跑一次。完整集合见 [install.md](skills/parallel-development/references/install.md)「每个门做什么」。真实违规阻塞；缺失工具降级为覆盖率注记（绝不静默绿）。
- **外环**（AI）：独立评审者对照冻结意图蓝图（用例 + 验收标准 + NFR）检查 diff——它抓到仅读代码 LLM 看不到的漂移。

**断路器。** 不同触发，不同动作（优先级：硬终止 > 升级 > 降级 > 挂起）：同一根因指纹 ≥ N=3 → **升级**（→ 外环）；内环迭代 ≥ M=8 → **降级**（→ 收窄范围）→ 预算 ≥ 80% 时**挂起**（→ 你）；**步上限 → 硬终止**（*能力*信号——`step-capped` → `not-yet`）；**token / 时间 / 成本上限 → 硬终止**（*资源*守卫——`resource-capped` → 能力上 `inconclusive`）。PreToolUse 钩子（`counters.py`）在状态进入终态后**拒绝**编辑——环无法冲过断路器；它是物理拦截，不是提示建议。

**蓝图漂移 → 硬回滚 + 反向提示注入。** 若 Coder 偏离原始意图（硬编码值过测试、静默丢弃用例），外环抓到后回滚到最后一个快照，**并注入反向提示**（丢失的用例 + 导致漂移的错误路径），使代理重新锚定原始目标。意图蓝图只读——仅经显式修订通道变更。

**恢复。** pd 的运行时状态 gitignored。会话中途结束，重进时从第一个未收敛条目恢复——无进度丢失。

**提交策略。** 默认 `auto-per-stage`（每个收敛阶段在特性分支上一条提交，永不 `main`，无需确认）。偏好自己提交时用 `loop_state.py init --commit manual` 覆盖。

## 速查

| 你想 | 提示 | 技能 |
| --- | --- | --- |
| 代码，单任务 | `implement …` | pd |
| 按计划写代码 | `implement feature X per @plan.md` | pd |
| 规范 / 架构设计 / 迭代计划 | `author a spec for …` | bc |
| 把文档交叉评审到收敛 | `cross-review this requirements doc @doc.md` | csr |
| 收敛 → 规格化 → 实现（带交叉评审） | (1) `/cross-source-review converge @reqs.md` → (2) `/blueprint-crafting author a spec …` → (3) `/parallel-development implement …` | csr → bc → pd |
| 规格化**且**实现 | (1) `/blueprint-crafting author a spec …` → (2) `/parallel-development implement per the frozen spec` | bc → pd |
| 一次性 bc → pd（**跳过规范评审**） | `Using @ctx.md, have /blueprint-crafting produce a spec, then /parallel-development implement it` | bc → pd（无评审——bc 的假设未经检查直接通过） |
| 代码 + 外部工具（Vale/Semgrep/…） | `/solidforge:arm-tools --scaffold-configs …` → `implement …` | pd + 工具 |
| 带设计治理的前端 | `/impeccable init` → `implement …` | pd + Impeccable |
| 异源（跨族）对抗评审 | `/solidforge:arm-tools` → 填 `.env.solidforge` → `hetero_review.py …`（省略 `--profile`；wrapper 用 `HETERO_PROFILE`，默认 deepseek——或条目 `hetero: on`） | pd + hetero |
| 修 / 重构 / 测试 / 文档 | `fix …` / `refactor …` / `write e2e tests …` / `document …` | pd |

---

*Solid Forge 是一个 Claude Code 插件。技能按描述激活；可靠性重要时显式调用（`/cross-source-review`、`/blueprint-crafting`、`/parallel-development`、`/solidforge:arm-tools`）。总览：[README.md](README.md)；权威安装与功能文档：[install.md](skills/parallel-development/references/install.md)；成熟度框架：[maturity.md](skills/parallel-development/references/maturity.md)。*
