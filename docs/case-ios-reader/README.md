# 案例：iOS 原生电子书阅读器 PRD（blueprint-crafting 实录）

这是 [start-from-requirements.zh-CN.md](../start-from-requirements.zh-CN.md) 使用的完整案例，展示从一句话需求到冻结 PRD 的全过程。

## 出发点

```text
/solidforge:blueprint-crafting 帮我写 PRD，我想做一个iOS原生电子书阅读器
```

案例日期 2026-09-16，全程 23 分 7 秒；外环（plan-reviewer）多轮评审累计修复 7 个缺陷，最终内环、外环均 0 Blocker 收敛。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| [product-spec.md](product-spec.md) | PRD 本体：16 条带 seam 声明的验收标准、8 条结果指标、8 个已定决策、4 个 deferred ODP |
| [product-spec.queue.md](product-spec.queue.md) | 冻结任务队列（16 项），交给 parallel-development 的握手件 |
| [product-spec.run-record.json](product-spec.run-record.json) | 收敛凭证（双字段裁决：process_converged / rightness） |
| [findings.json](findings.json) | 外环 plan-reviewer 的 findings（编号排到 novel-7；末轮剩 2 条 warning，对应修复已回写进 spec 与 plan-model） |
| [plan-model.json](plan-model.json) | 喂给 produce.py 的 plan-model（anchors 为 author-supplied） |
| [images/](images/) | 会话截图 s1–s5：分步访谈问卷四张 + 收敛结果页一张 |

## 拷贝声明

以上文件是从产出仓库逐字拷贝，未做任何内容修改（本 README 除外）。文件内部出现的相对路径（如 `docs/product-spec.md`、`authority_chain` 条目）指向原仓库的目录布局，在本案例目录下不对应实际文件，读时按原布局理解即可。
